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


def test_pcs_with_pcs_stock():
    """2 pcs of tomatoes available, 1 pcs required should cover."""
    assert run(1, "pcs", [(7, 2, "pcs")]) == []


def test_pcs_insufficient_pcs_stock():
    """3 pcs required but only 2 pcs available."""
    result = run(3, "pcs", [(7, 2, "pcs")])
    assert result[0]["missing_quantity"] == 1
    assert result[0]["available_quantity"] == 2


def test_pcs_vs_grams_incompatible():
    """pcs (individual items) cannot be compared to g (weight)."""
    result = run(100, "g", [(7, 1, "pcs")])
    assert result[0]["available_quantity"] == 0
    assert result[0]["incompatible_units"] == ["pcs"]


def test_pcs_vs_unit_incompatible():
    """pcs (individual items) cannot be compared to unit (retail packages).
    When unit is converted to g via pack_size, incompatible_units shows the base unit.
    """
    result = run(2, "pcs", [(7, 1, "unit", "400g")])
    assert result[0]["available_quantity"] == 0
    assert result[0]["incompatible_units"] == ["g"]


def test_grams_vs_pcs_incompatible():
    """g (weight) cannot be compared to pcs (individual items)."""
    result = run(1, "pcs", [(7, 500, "g")])
    assert result[0]["available_quantity"] == 0
    assert result[0]["incompatible_units"] == ["g"]


def test_unit_pack_to_grams():
    """1 unit of 1kg product = 1000g, satisfies 800g requirement."""
    assert run(800, "g", [(7, 1, "unit", "1kg")]) == []


def test_unit_multiple_packs():
    """2 units of 400g product = 800g."""
    assert run(800, "g", [(7, 2, "unit", "400g")]) == []


def test_balalam_scenario_same_type_incompatible_units():
    """Regression test: inventory stock exists but in incompatible units.

    Scenario:
    - Product (Badedas) has ingredient_type_id=18 (Balalam) with 491ml in stock
    - Meal requires 250g of ingredient_type_id=18 (Balalam)
    - Meal requires 3 pcs of ingredient_type_id=18 (Balalam)

    Expected:
    - Both ingredients report as missing (ml is incompatible with g and pcs)
    - But incompatible_units shows ['ml'] (stock exists, just incompatible)
    """
    ingredients = [
        (11, "Bubbles", 18, "Balalam", 250.0, "g"),
        (11, "Bubbles", 18, "Balalam", 3.0, "pcs"),
    ]
    stock = [
        (18, 491.0, "ml", "200ml"),
    ]
    result = calculate_shortages(ingredients, stock)

    assert len(result) == 2

    for shortage in result:
        assert shortage["ingredient_type_id"] == 18
        assert shortage["ingredient_type_name"] == "Balalam"
        assert shortage["available_quantity"] == 0.0
        assert shortage["missing_quantity"] > 0
        assert shortage["incompatible_units"] == ["ml"]


def test_duplicate_ingredient_same_type_single_source():
    """Test: one inventory source, duplicate meal requirement.
    
    Inventory: Bread = 250g
    Meal:
      Bread = 250g
      Bread = 250g
    
    Expected:
    - first available = 250g
    - second available = 0g
    - second missing = 250g
    - total missing = 250g
    """
    ingredients = [
        (1, "Sandwich", 7, "Bread", 250.0, "g"),
        (1, "Sandwich", 7, "Bread", 250.0, "g"),
    ]
    stock = [
        (7, 250.0, "g"),
    ]
    result = calculate_shortages(ingredients, stock)
    
    assert len(result) == 1
    assert result[0]["required_quantity"] == 250.0
    assert result[0]["available_quantity"] == 0.0
    assert result[0]["missing_quantity"] == 250.0


def test_duplicate_ingredient_enough_stock():
    """Test: enough stock for duplicate requirements.
    
    Inventory: Bread = 500g
    Meal:
      Bread = 250g
      Bread = 250g
    
    Expected: total missing = 0g
    """
    ingredients = [
        (1, "Sandwich", 7, "Bread", 250.0, "g"),
        (1, "Sandwich", 7, "Bread", 250.0, "g"),
    ]
    stock = [
        (7, 500.0, "g"),
    ]
    result = calculate_shortages(ingredients, stock)
    
    assert result == []


def test_duplicate_ingredient_multiple_sources():
    """Test: multiple inventory sources, duplicate requirements.
    
    Inventory:
      Bread A = 250g
      Bread B = 250g
    Meal:
      Bread = 300g
      Bread = 300g
    
    Expected:
    - total available = 500g
    - total required = 600g
    - total missing = 100g
    """
    ingredients = [
        (1, "Sandwich", 7, "Bread", 300.0, "g"),
        (1, "Sandwich", 7, "Bread", 300.0, "g"),
    ]
    stock = [
        (7, 250.0, "g"),
        (7, 250.0, "g"),
    ]
    result = calculate_shortages(ingredients, stock)
    
    assert len(result) == 1
    assert result[0]["required_quantity"] == 300.0
    assert result[0]["available_quantity"] == 200.0
    assert result[0]["missing_quantity"] == 100.0


def test_different_ingredient_types_independent():
    """Test: different ingredient types remain independent.
    
    Inventory:
      Bread = 250g
      Milk = 500ml
    Meal:
      Bread = 250g
      Milk = 500ml
    
    Both should be fully satisfied.
    """
    ingredients = [
        (1, "Breakfast", 7, "Bread", 250.0, "g"),
        (1, "Breakfast", 8, "Milk", 500.0, "ml"),
    ]
    stock = [
        (7, 250.0, "g"),
        (8, 500.0, "ml"),
    ]
    result = calculate_shortages(ingredients, stock)
    
    assert result == []


def test_duplicate_ingredient_incompatible_units():
    """Test: incompatible units in duplicate requirements.
    
    Inventory: Bread = 250g
    Meal:
      Bread = 3pcs
      Bread = 3pcs
    
    Should NOT invent a conversion from grams to pieces.
    Both requirements should report as missing.
    """
    ingredients = [
        (1, "Sandwich", 7, "Bread", 3.0, "pcs"),
        (1, "Sandwich", 7, "Bread", 3.0, "pcs"),
    ]
    stock = [
        (7, 250.0, "g"),
    ]
    result = calculate_shortages(ingredients, stock)
    
    assert len(result) == 2
    for shortage in result:
        assert shortage["available_quantity"] == 0.0
        assert shortage["missing_quantity"] == 3.0
        assert shortage["incompatible_units"] == ["g"]


def test_duplicate_unit_packs_with_conversion():
    """Test: unit packs that convert to base unit, duplicate requirements.
    
    Inventory: Bread = 2 units of 400g each = 800g total
    Meal:
      Bread = 500g
      Bread = 300g
    
    Expected: total available = 800g, total required = 800g, missing = 0g
    """
    ingredients = [
        (1, "Meal1", 7, "Bread", 500.0, "g"),
        (1, "Meal1", 7, "Bread", 300.0, "g"),
    ]
    stock = [
        (7, 2, "unit", "400g"),
    ]
    result = calculate_shortages(ingredients, stock)
    
    assert result == []


def test_buy_bread_check_shortages_no_manual_conversion():
    """End-to-end: User buys bread (1 unit of 500g), creates meal (250g).
    
    No manual conversion needed. The system knows:
    - Inventory: 1 unit of Bread
    - Product: Bread has pack_size = 500g
    - Meal: requires 250g Bread
    
    Should calculate available = 500g, missing = 0g
    """
    ingredients = [
        (1, "Lunch", 7, "Bread", 250.0, "g"),
    ]
    stock = [
        (7, 1, "unit", "500g"),
    ]
    result = calculate_shortages(ingredients, stock)
    assert result == []


def test_buy_milk_check_shortages_with_ml():
    """End-to-end: User buys milk (2 units of 1L each), creates meal (750ml).
    
    Inventory: 2 units of Milk (Product says 1L per unit)
    Meal: requires 750ml Milk
    
    Should calculate available = 2000ml, missing = 0ml (1250ml remaining)
    """
    ingredients = [
        (1, "Breakfast", 8, "Milk", 750.0, "ml"),
    ]
    stock = [
        (8, 2, "unit", "1l"),
    ]
    result = calculate_shortages(ingredients, stock)
    assert result == []


def test_buy_pasta_exact_fit():
    """User buys pasta (1 unit of 500g), meal requires exactly 500g."""
    ingredients = [
        (1, "Dinner", 9, "Pasta", 500.0, "g"),
    ]
    stock = [
        (9, 1, "unit", "500g"),
    ]
    result = calculate_shortages(ingredients, stock)
    assert result == []


def test_buy_pasta_shortage():
    """User buys pasta (1 unit of 500g), meal requires 600g."""
    ingredients = [
        (1, "Dinner", 9, "Pasta", 600.0, "g"),
    ]
    stock = [
        (9, 1, "unit", "500g"),
    ]
    result = calculate_shortages(ingredients, stock)
    assert len(result) == 1
    assert result[0]["missing_quantity"] == 100


def test_duplicate_requirements_with_unit_packs():
    """Inventory: 1 unit of 500g Bread.
    Meal has two Bread requirements: 250g + 250g.
    
    Allocation should work:
    - Requirement 1: 250g from 500g available, 250g remaining
    - Requirement 2: 250g from 250g remaining, 0g remaining
    - Result: both fully satisfied, no shortage
    """
    ingredients = [
        (1, "Sandwich", 7, "Bread", 250.0, "g"),
        (1, "Sandwich", 7, "Bread", 250.0, "g"),
    ]
    stock = [
        (7, 1, "unit", "500g"),
    ]
    result = calculate_shortages(ingredients, stock)
    assert result == []


def test_duplicate_requirements_insufficient_unit_packs():
    """Inventory: 1 unit of 500g Bread.
    Meal has two Bread requirements: 300g + 300g = 600g total.
    
    Available = 500g, required = 600g
    Allocation:
    - Requirement 1: 300g from 500g available, 200g remaining
    - Requirement 2: needs 300g but only 200g remaining
    - Result: second requirement shows 200g available, 100g missing
    """
    ingredients = [
        (1, "Sandwich", 7, "Bread", 300.0, "g"),
        (1, "Sandwich", 7, "Bread", 300.0, "g"),
    ]
    stock = [
        (7, 1, "unit", "500g"),
    ]
    result = calculate_shortages(ingredients, stock)
    assert len(result) == 1
    assert result[0]["required_quantity"] == 300.0
    assert result[0]["available_quantity"] == 200.0
    assert result[0]["missing_quantity"] == 100.0


def test_multiple_unit_packs_cover_duplicate_requirements():
    """Inventory: 2 units of 400g Bread (total 800g).
    Meal: 400g + 400g Bread.
    
    Should be fully satisfied.
    """
    ingredients = [
        (1, "Meal1", 7, "Bread", 400.0, "g"),
        (1, "Meal1", 7, "Bread", 400.0, "g"),
    ]
    stock = [
        (7, 2, "unit", "400g"),
    ]
    result = calculate_shortages(ingredients, stock)
    assert result == []


def test_eggs_per_pack_incompatible_without_parser():
    """Eggs: 6 per pack. If parser can't extract this, stays incompatible.
    
    Inventory: 1 unit (can't be converted to pcs)
    Meal: 3 pcs
    
    Should be incompatible.
    """
    ingredients = [
        (1, "Breakfast", 10, "Eggs", 3.0, "pcs"),
    ]
    stock = [
        (10, 1, "unit", "6 per pack"),
    ]
    result = calculate_shortages(ingredients, stock)
    assert len(result) == 1
    assert result[0]["available_quantity"] == 0
    assert result[0]["incompatible_units"] == ["unit"]


def test_multipack_unit_conversion():
    """Tomatoes: 2 x 400g pack (800g total).
    Inventory: 1 unit
    Meal: 500g
    
    Available = 800g, required = 500g, missing = 0g
    """
    ingredients = [
        (1, "Dinner", 11, "Tomatoes", 500.0, "g"),
    ]
    stock = [
        (11, 1, "unit", "2 x 400g"),
    ]
    result = calculate_shortages(ingredients, stock)
    assert result == []
