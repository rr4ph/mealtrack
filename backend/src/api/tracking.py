import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from backend.database.connections import get_connection
from backend.src.utils.auth import current_user_id, require_meal_owner
from backend.src.utils.consumption import plan_consumption
from backend.src.utils.shortages import convert_quantity

router = APIRouter()


class GoalsAPI(BaseModel):
    daily_calorie_goal: int | None = None
    spending_limit: float | None = None


class MealCaloriesUpdate(BaseModel):
    calories_per_serving: float | None = None


class PurchaseCreate(BaseModel):
    product_id: int
    quantity: float
    price_paid: float
    purchased_at: datetime.datetime | None = None


class ConsumeCreate(BaseModel):
    servings: float = 1
    consumed_at: datetime.datetime | None = None


@router.get("/goals", response_model=GoalsAPI)
def get_goals(user_id: int = Depends(current_user_id)):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT daily_calorie_goal, spending_limit FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return GoalsAPI(
        daily_calorie_goal=row[0],
        spending_limit=float(row[1]) if row[1] is not None else None
    )


@router.put("/goals", response_model=GoalsAPI)
def update_goals(data: GoalsAPI, user_id: int = Depends(current_user_id)):
    if data.daily_calorie_goal is not None and not 500 <= data.daily_calorie_goal <= 10000:
        raise HTTPException(status_code=400, detail="Calorie goal must be between 500 and 10,000 kcal.")
    if data.spending_limit is not None and not 0 <= data.spending_limit <= 100000:
        raise HTTPException(status_code=400, detail="Spending limit must be between 0 and 100,000.")
    limit = round(data.spending_limit, 2) if data.spending_limit is not None else None
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET daily_calorie_goal = %s, spending_limit = %s WHERE user_id = %s",
                (data.daily_calorie_goal, limit, user_id)
            )
    return GoalsAPI(daily_calorie_goal=data.daily_calorie_goal, spending_limit=limit)


@router.delete("/goals/spending-limit")
def reset_spending_limit(user_id: int = Depends(current_user_id)):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET spending_limit = NULL, budget_reset_at = now() WHERE user_id = %s", (user_id,))
    return {"spending_limit": None}


@router.delete("/consumptions/today")
def reset_todays_consumption(user_id: int = Depends(current_user_id)):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM meal_consumptions WHERE user_id = %s AND consumed_at >= current_date AND consumed_at < current_date + 1",
                (user_id,)
            )
            return {"deleted": cursor.rowcount}


@router.get("/meals/{meal_id}/calories", dependencies=[Depends(require_meal_owner)])
def get_meal_calories(meal_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT calories_per_serving FROM meals WHERE meal_id = %s", (meal_id,))
            value = cursor.fetchone()[0]
    return {"calories_per_serving": float(value) if value is not None else None}


@router.put("/meals/{meal_id}/calories", dependencies=[Depends(require_meal_owner)])
def update_meal_calories(meal_id: int, data: MealCaloriesUpdate):
    value = data.calories_per_serving
    if value is not None and not 0 <= value <= 10000:
        raise HTTPException(status_code=400, detail="Calories must be between 0 and 10,000.")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE meals SET calories_per_serving = %s WHERE meal_id = %s", (value, meal_id))
    return {"calories_per_serving": value}


@router.get("/meals/{meal_id}/consume-preview", dependencies=[Depends(require_meal_owner)])
def preview_consumption(meal_id: int, servings: float = 1, user_id: int = Depends(current_user_id)):
    if not 0 < servings <= 100:
        raise HTTPException(status_code=400, detail="Servings must be greater than 0 and at most 100.")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT calories_per_serving FROM meals WHERE meal_id = %s", (meal_id,))
            per_serving = cursor.fetchone()[0]
            lines, _ = plan_consumption(cursor, meal_id, user_id, servings)
    return {
        "servings": servings,
        "calories": round(float(per_serving) * servings, 2) if per_serving is not None else None,
        "sufficient": all(line["status"] == "ok" for line in lines),
        "lines": lines,
    }


@router.post("/meals/{meal_id}/consume", dependencies=[Depends(require_meal_owner)])
def consume_meal(meal_id: int, data: ConsumeCreate, user_id: int = Depends(current_user_id)):
    if not 0 < data.servings <= 100:
        raise HTTPException(status_code=400, detail="Servings must be greater than 0 and at most 100.")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name, calories_per_serving FROM meals WHERE meal_id = %s", (meal_id,))
            name, per_serving = cursor.fetchone()
            if per_serving is None:
                raise HTTPException(status_code=400, detail="Set calories per serving before logging this meal.")
            lines, deductions = plan_consumption(cursor, meal_id, user_id, data.servings, lock=True)
            for product_id, new_quantity in deductions:
                cursor.execute(
                    """
                    UPDATE inventory_items SET quantity = %s
                    WHERE product_id = %s
                      AND inventory_id = (SELECT inventory_id FROM user_inventories WHERE user_id = %s)
                    """,
                    (round(new_quantity, 3), product_id, user_id)
                )
            cursor.execute(
                """
                INSERT INTO meal_consumptions(user_id, meal_id, meal_name, servings, calories, consumed_at)
                VALUES (%s, %s, %s, %s, %s, COALESCE(%s, now()))
                RETURNING consumption_id, calories, consumed_at
                """,
                (user_id, meal_id, name, data.servings, round(float(per_serving) * data.servings, 2), data.consumed_at)
            )
            row = cursor.fetchone()
    return {
        "consumption_id": row[0], "calories": float(row[1]), "consumed_at": row[2].isoformat(),
        "sufficient": all(line["status"] == "ok" for line in lines), "lines": lines,
    }


@router.post("/purchases")
def create_purchase(data: PurchaseCreate, user_id: int = Depends(current_user_id)):
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")
    if not 0 <= data.price_paid <= 100000:
        raise HTTPException(status_code=400, detail="Price paid must be a non-negative amount.")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT currency, pack_size FROM products WHERE product_id = %s", (data.product_id,))
            product = cursor.fetchone()
            if product is None:
                raise HTTPException(status_code=404, detail="Product not found.")
            cursor.execute("SELECT inventory_id FROM user_inventories WHERE user_id = %s", (user_id,))
            inventory_id = cursor.fetchone()[0]
            cursor.execute(
                "SELECT quantity_unit FROM inventory_items WHERE inventory_id = %s AND product_id = %s FOR UPDATE",
                (inventory_id, data.product_id)
            )
            existing = cursor.fetchone()
            if existing is None:
                cursor.execute(
                    "INSERT INTO inventory_items(inventory_id, product_id, quantity, quantity_unit) VALUES (%s,%s,%s,'unit')",
                    (inventory_id, data.product_id, data.quantity)
                )
            else:
                add = convert_quantity(data.quantity, "unit", existing[0], product[1])
                if add is None:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Can't add packs to your stock recorded in {existing[0]}. Edit that item's unit first."
                    )
                cursor.execute(
                    "UPDATE inventory_items SET quantity = quantity + %s WHERE inventory_id = %s AND product_id = %s",
                    (add, inventory_id, data.product_id)
                )
            cursor.execute(
                """
                INSERT INTO purchases(user_id, product_id, quantity, quantity_unit, price_paid, currency, purchased_at)
                VALUES (%s, %s, %s, 'unit', %s, %s, COALESCE(%s, now()))
                RETURNING purchase_id
                """,
                (user_id, data.product_id, data.quantity, round(data.price_paid, 2), product[0], data.purchased_at)
            )
            purchase_id = cursor.fetchone()[0]
    return {"purchase_id": purchase_id, "message": "Purchase recorded."}


_RANGES = {
    "daily": ("day", 7),
    "weekly": ("week", 4),
    "monthly": ("month", 6),
}
_SOURCES = {
    "calories": ("meal_consumptions", "consumed_at", "calories"),
    "spending": ("purchases", "purchased_at", "price_paid"),
}


def _bucket_start(date, unit):
    if unit == "week":
        return date - datetime.timedelta(days=date.weekday())
    if unit == "month":
        return date.replace(day=1)
    return date


def _previous(date, unit, steps):
    if unit == "day":
        return date - datetime.timedelta(days=steps)
    if unit == "week":
        return date - datetime.timedelta(weeks=steps)
    month = date.month - 1 - steps
    return date.replace(year=date.year + month // 12, month=month % 12 + 1, day=1)


def _next(date, unit):
    if unit == "day":
        return date + datetime.timedelta(days=1)
    if unit == "week":
        return date + datetime.timedelta(weeks=1)
    return _previous(date, "month", -1)


def _label(date, unit):
    if unit == "month":
        return date.strftime("%b")
    if unit == "week":
        return f"{date.day} {date.strftime('%b')}"
    return f"{date.strftime('%a')} {date.day}"


@router.get("/stats/{metric}")
def get_stats(
    metric: str,
    time_range: str = Query("daily", alias="range"),
    user_id: int = Depends(current_user_id),
):
    if metric not in _SOURCES or time_range not in _RANGES:
        raise HTTPException(status_code=400, detail="Unknown metric or range.")
    table, time_col, value_col = _SOURCES[metric]
    unit, count = _RANGES[time_range]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_date")
            today = cursor.fetchone()[0]
            first = _previous(_bucket_start(today, unit), unit, count - 1)
            cursor.execute(
                f"""
                SELECT date_trunc(%s, {time_col})::date, SUM({value_col})
                FROM {table}
                WHERE user_id = %s AND {time_col} >= %s
                GROUP BY 1
                """,
                (unit, user_id, first)
            )
            sums = {row[0]: float(row[1]) for row in cursor.fetchall()}

            month_start = today.replace(day=1)
            cursor.execute(
                f"SELECT COALESCE(SUM({value_col}), 0) FROM {table} WHERE user_id = %s AND {time_col} >= %s",
                (user_id, today if metric == "calories" else month_start)
            )
            period_total = float(cursor.fetchone()[0])
            cursor.execute(
                "SELECT daily_calorie_goal, spending_limit FROM users WHERE user_id = %s", (user_id,)
            )
            goals = cursor.fetchone()
            budget_spent = 0.0
            if metric == "spending":
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(pu.price_paid), 0) FROM purchases pu, users u
                    WHERE u.user_id = %s AND pu.user_id = u.user_id
                      AND pu.purchased_at >= GREATEST(%s::timestamp, COALESCE(u.budget_reset_at, %s::timestamp))
                    """,
                    (user_id, month_start, month_start)
                )
                budget_spent = float(cursor.fetchone()[0])

    points = []
    start = first
    for _ in range(count):
        total = sums.get(start, 0.0)
        value = total
        if metric == "calories" and unit != "day":
            days = (min(_next(start, unit), today + datetime.timedelta(days=1)) - start).days
            value = total / max(days, 1)
        points.append({
            "start": start.isoformat(),
            "label": _label(start, unit),
            "total": round(total, 2),
            "value": round(value, 2),
        })
        start = _next(start, unit)

    if metric == "calories":
        goal = goals[0]
        return {
            "metric": metric, "range": time_range, "points": points,
            "goal": goal, "today": round(period_total, 2),
            "average_per_day": unit != "day",
        }
    limit = float(goals[1]) if goals[1] is not None else None
    return {
        "metric": metric, "range": time_range, "points": points,
        "limit": limit, "spent": round(period_total, 2),
        "budget_spent": round(budget_spent, 2),
        "remaining": round(limit - budget_spent, 2) if limit is not None else None,
    }


@router.get("/activity/{metric}")
def get_activity(
    metric: str,
    time_range: str = Query("daily", alias="range"),
    user_id: int = Depends(current_user_id),
):
    if metric not in _SOURCES or time_range not in _RANGES:
        raise HTTPException(status_code=400, detail="Unknown metric or range.")
    unit = _RANGES[time_range][0]
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_date")
            start = _bucket_start(cursor.fetchone()[0], unit)
            if metric == "calories":
                cursor.execute(
                    """
                    SELECT consumption_id, meal_name, calories, consumed_at
                    FROM meal_consumptions WHERE user_id = %s AND consumed_at >= %s
                    ORDER BY consumed_at DESC LIMIT 100
                    """,
                    (user_id, start)
                )
                return [
                    {"id": r[0], "name": r[1], "amount": float(r[2]), "at": r[3].isoformat(), "detail": None}
                    for r in cursor.fetchall()
                ]
            cursor.execute(
                """
                SELECT pu.purchase_id, p.name, pu.price_paid, pu.purchased_at, p.supermarket
                FROM purchases pu JOIN products p ON p.product_id = pu.product_id
                WHERE pu.user_id = %s AND pu.purchased_at >= %s
                ORDER BY pu.purchased_at DESC LIMIT 100
                """,
                (user_id, start)
            )
            return [
                {"id": r[0], "name": r[1], "amount": float(r[2]), "at": r[3].isoformat(), "detail": r[4]}
                for r in cursor.fetchall()
            ]
