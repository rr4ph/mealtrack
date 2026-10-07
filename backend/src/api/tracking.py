import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from backend.database.connections import get_connection
from backend.src.utils.auth import current_user_id, require_meal_owner
from backend.src.utils.consumption import plan_consumption

router = APIRouter()


class GoalsAPI(BaseModel):
    daily_calorie_goal: int | None = None


class MealCaloriesUpdate(BaseModel):
    calories_per_serving: float | None = None


class ConsumeCreate(BaseModel):
    servings: float = 1
    consumed_at: datetime.datetime | None = None


@router.get("/goals", response_model=GoalsAPI)
def get_goals(user_id: int = Depends(current_user_id)):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT daily_calorie_goal FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return GoalsAPI(daily_calorie_goal=row[0])


@router.put("/goals", response_model=GoalsAPI)
def update_goals(data: GoalsAPI, user_id: int = Depends(current_user_id)):
    if data.daily_calorie_goal is not None and not 500 <= data.daily_calorie_goal <= 10000:
        raise HTTPException(status_code=400, detail="Calorie goal must be between 500 and 10,000 kcal.")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET daily_calorie_goal = %s WHERE user_id = %s",
                (data.daily_calorie_goal, user_id)
            )
    return GoalsAPI(daily_calorie_goal=data.daily_calorie_goal)


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


_RANGES = {
    "daily": ("day", 7),
    "weekly": ("week", 4),
    "monthly": ("month", 6),
}
_SOURCES = {
    "calories": ("meal_consumptions", "consumed_at", "calories"),
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

            cursor.execute(
                f"SELECT COALESCE(SUM({value_col}), 0) FROM {table} WHERE user_id = %s AND {time_col} >= %s",
                (user_id, today)
            )
            period_total = float(cursor.fetchone()[0])
            cursor.execute("SELECT daily_calorie_goal FROM users WHERE user_id = %s", (user_id,))
            goals = cursor.fetchone()

    points = []
    start = first
    for _ in range(count):
        total = sums.get(start, 0.0)
        value = total
        if unit != "day":
            days = (min(_next(start, unit), today + datetime.timedelta(days=1)) - start).days
            value = total / max(days, 1)
        points.append({
            "start": start.isoformat(),
            "label": _label(start, unit),
            "total": round(total, 2),
            "value": round(value, 2),
        })
        start = _next(start, unit)

    return {
        "metric": metric, "range": time_range, "points": points,
        "goal": goals[0], "today": round(period_total, 2),
        "average_per_day": unit != "day",
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
