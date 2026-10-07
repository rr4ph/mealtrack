from backend.src.utils.shortages import normalise_unit, stock_base_amount

EPSILON = 1e-9


def _round(value):
    return round(value + 0.0, 4)


def plan_consumption(cursor, meal_id, user_id, servings, lock=False):
    """Work out which inventory each ingredient consumes for the given servings.

    Pools stock the same way as the shortage logic: a product only counts when its
    stock converts to the ingredient's base unit. Several matching inventory
    products are consumed in product_id order.
    Returns (lines, deductions) where deductions is [(product_id, new_quantity)].
    """
    cursor.execute(
        """
        SELECT t.ingredient_type_id, t.name, i.quantity, i.quantity_unit
        FROM ingredients i
        JOIN ingredient_types t ON t.ingredient_type_id = i.ingredient_type_id
        WHERE i.meal_id = %s
        ORDER BY i.ingredient_id
        """,
        (meal_id,)
    )
    ingredients = cursor.fetchall()
    cursor.execute(
        f"""
        SELECT p.ingredient_type_id, p.product_id, p.name, ii.quantity, ii.quantity_unit, p.pack_size
        FROM user_inventories inv
        JOIN inventory_items ii ON ii.inventory_id = inv.inventory_id
        JOIN products p ON p.product_id = ii.product_id
        WHERE inv.user_id = %s AND p.ingredient_type_id IS NOT NULL
        ORDER BY p.product_id
        {"FOR UPDATE OF ii" if lock else ""}
        """,
        (user_id,)
    )
    stock = cursor.fetchall()

    lines = []
    deductions = []
    for type_id, type_name, quantity, unit in ingredients:
        base, factor = normalise_unit(unit)
        required = float(quantity) * float(servings)
        candidates = []
        for s_type, product_id, product_name, s_qty, s_unit, pack in stock:
            if s_type != type_id:
                continue
            s_base, amount = stock_base_amount(s_qty, s_unit, pack)
            if s_base == base and amount > 0:
                candidates.append((product_id, product_name, float(s_qty), amount))

        line = {
            "ingredient_type_id": type_id,
            "ingredient_type_name": type_name,
            "product_id": None,
            "product_name": None,
            "quantity_unit": unit,
            "required": _round(required),
            "available": 0.0,
            "will_use": 0.0,
            "remaining": None,
            "missing": _round(required),
            "status": "short",
            "candidates": [],
        }
        if candidates:
            available = sum(c[3] for c in candidates) / factor
            left = min(required, available) * factor
            used_parts = []
            for product_id, product_name, s_qty, amount in candidates:
                take = min(left, amount)
                left -= take
                if take <= EPSILON:
                    continue
                new_base = amount - take
                new_qty = 0.0 if new_base < EPSILON else s_qty * new_base / amount
                deductions.append((product_id, new_qty))
                used_parts.append({
                    "product_name": product_name,
                    "before": _round(amount / factor),
                    "used": _round(take / factor),
                    "after": _round((amount - take) / factor),
                })
            used = min(required, available)
            line.update(
                product_id=candidates[0][0],
                product_name=", ".join(u["product_name"] for u in used_parts) or candidates[0][1],
                products=used_parts,
                available=_round(available),
                will_use=_round(used),
                remaining=_round(available - used),
                missing=_round(max(required - available, 0)),
                status="ok" if required - available <= EPSILON else "short",
            )
        lines.append(line)
    return lines, deductions
