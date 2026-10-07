import re

_UNITS = {
    "g": ("g", 1),
    "kg": ("g", 1000),
    "ml": ("ml", 1),
    "l": ("ml", 1000),
    "pcs": ("pcs", 1),
}


_PACK_RE = re.compile(
    r"^\s*(?:(\d+)\s*x\s*)?(\d+(?:\.\d+)?)\s*(kg|g|ml|l|litres?|liters?|pcs|pc|pieces?|items?)\s*$",
    re.IGNORECASE,
)


def parse_pack_size(pack_size):
    """Return (base_unit, amount) for sizes like '400g' or '2 x 140g', else None."""
    match = _PACK_RE.match(pack_size or "")
    if not match:
        return None
    count, amount, unit = match.groups()
    unit = unit.lower()
    if unit.startswith(("litre", "liter")):
        unit = "l"
    elif unit in ("pc", "piece", "pieces", "item", "items"):
        unit = "pcs"
    base, factor = _UNITS[unit]
    total = int(count or 1) * float(amount) * factor
    return (base, total) if total > 0 else None


def normalise_unit(unit):
    key = (unit or "").strip().lower()
    return _UNITS.get(key, (key, 1))


def stock_base_amount(quantity, unit, pack_size=None):
    """Return (base_unit, amount); "unit" is expanded via pack size when parseable.

    For "pcs" (individual items), quantity is returned as-is without conversion.
    """
    base, factor = normalise_unit(unit)
    amount = float(quantity) * factor
    if base == "unit":
        pack = parse_pack_size(pack_size)
        if pack:
            base, pack_amount = pack
            amount = float(quantity) * pack_amount
    return base, amount


def convert_quantity(quantity, from_unit, to_unit, pack_size=None):
    """Convert a quantity between units, or return None if not cleanly known.

    Rules:
    - pcs only converts to pcs (no weight/volume estimation)
    - g/kg conversions work within weight base
    - ml/l conversions work within volume base
    - unit converts using pack_size when available
    """
    base, amount = stock_base_amount(quantity, from_unit, pack_size)
    to_base, to_factor = normalise_unit(to_unit)
    if to_base == "unit":
        if base == "unit":
            return float(quantity)
        pack = parse_pack_size(pack_size)
        if not pack or pack[0] != base:
            return None
        count = amount / pack[1]
        return float(round(count)) if abs(count - round(count)) < 1e-6 else None
    if to_base != base:
        return None
    return amount / to_factor


def calculate_shortages(ingredients, stock):
    """ingredients: (meal_id, meal_name, type_id, type_name, quantity, unit)
    stock: (type_id, quantity, unit[, pack_size])

    Stock only counts when its unit is convertible to the ingredient's unit.
    - pcs stock only matches pcs ingredients
    - weight/volume conversions work (g/kg, ml/l)
    - unit stock is converted using the product's pack size when parseable
    - incompatible units are listed (e.g., pcs vs g, pcs vs unit)
    
    Allocation tracking: inventory is allocated in order to ingredients in the meal.
    Once allocated to one ingredient, that portion is not available to later ingredients.
    """
    available_by_type = {}
    for type_id, quantity, unit, *rest in stock:
        base, amount = stock_base_amount(quantity, unit, rest[0] if rest else None)
        per_unit = available_by_type.setdefault(type_id, {})
        per_unit[base] = per_unit.get(base, 0) + amount

    remaining_by_type = {}
    for type_id, bases in available_by_type.items():
        remaining_by_type[type_id] = bases.copy()

    shortages = []
    for meal_id, meal_name, type_id, type_name, quantity, unit in ingredients:
        base, factor = normalise_unit(unit)
        required = float(quantity)
        have = available_by_type.get(type_id, {})
        remaining = remaining_by_type.get(type_id, {})
        
        available_amount = remaining.get(base, 0)
        available = available_amount / factor
        
        if required > available:
            shortages.append({
                "meal_id": meal_id,
                "meal_name": meal_name,
                "ingredient_type_id": type_id,
                "ingredient_type_name": type_name,
                "required_quantity": required,
                "available_quantity": available,
                "missing_quantity": required - available,
                "quantity_unit": unit,
                "incompatible_units": sorted(u for u in have if u != base),
            })
            allocated = available_amount
        else:
            allocated = required * factor
        
        if base not in remaining:
            remaining[base] = 0
        remaining[base] -= allocated
    
    return shortages
