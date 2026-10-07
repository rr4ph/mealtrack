from backend.src.utils.shortages import calculate_shortages, parse_pack_size


def run(required, unit, stock):
    return calculate_shortages([(1, "Meal", 7, "Tomato", required, unit)], stock)


def test_one_pack_covers_smaller_requirement():
    assert run(300, "g", [(7, 1, "unit", "400g")]) == []


def test_one_pack_short_by_100g():
    result = run(500, "g", [(7, 1, "unit", "400g")])
    assert result[0]["missing_quantity"] == 100


def test_two_packs_cover_requirement():
    assert run(700, "g", [(7, 2, "unit", "400g")]) == []


def test_multipack_and_kg_pack_sizes():
    assert parse_pack_size("2 x 140g") == ("g", 280)
    assert parse_pack_size("1kg") == ("g", 1000)


def test_unparseable_pack_size_stays_incompatible():
    result = run(100, "g", [(7, 1, "unit", "6 per pack")])
    assert result[0]["available_quantity"] == 0
    assert result[0]["incompatible_units"] == ["unit"]


def test_existing_unit_conversions():
    assert run(500, "g", [(7, 1, "kg")]) == []
    assert run(500, "ml", [(7, 1, "l")]) == []
    assert run(1, "kg", [(7, 500, "g")])[0]["missing_quantity"] == 0.5
