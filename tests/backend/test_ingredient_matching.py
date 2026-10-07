from backend.src.classes.product import Product
from backend.src.utils.enums import SupermarketType
from backend.src.utils.ingredient_matching import best_ingredient_type_id

TYPES = [(1, "Milk"), (2, "Chicken Breast"), (3, "Butter")]


def test_confident_match_is_assigned():
    product = {"name": "Semi Skimmed Milk 2L", "category": []}
    assert best_ingredient_type_id(product, TYPES) == 1


def test_unrelated_product_gets_no_type():
    product = {"name": "Chocolate Digestive Biscuits", "category": []}
    assert best_ingredient_type_id(product, TYPES) is None


def test_partial_multiword_match_is_rejected():
    product = {"name": "Chicken Thigh Fillets", "category": []}
    assert best_ingredient_type_id(product, TYPES) is None


def test_auto_assign_sets_type_and_keeps_explicit_one(monkeypatch):
    monkeypatch.setattr(
        "backend.src.classes.product.get_ingredient_types",
        lambda connection_choice: TYPES,
    )
    product = Product("Salted Butter 250g", 2.0, "GBP", SupermarketType.TESCO)
    product.auto_assign_ingredient_type()
    assert product.ingredient_type_id == 3

    explicit = Product("Salted Butter", 2.0, "GBP", SupermarketType.TESCO, ingredient_type_id=9)
    explicit.auto_assign_ingredient_type()
    assert explicit.ingredient_type_id == 9


def test_auto_assign_leaves_null_without_confident_match(monkeypatch):
    monkeypatch.setattr(
        "backend.src.classes.product.get_ingredient_types",
        lambda connection_choice: TYPES,
    )
    product = Product("Orange Juice", 1.0, "GBP", SupermarketType.TESCO)
    product.auto_assign_ingredient_type()
    assert product.ingredient_type_id is None


def test_plural_and_variant_matches():
    types = [(1, "Tomato"), (2, "Potato"), (3, "Pepper"), (4, "Chicken")]
    cases = {
        "Morrisons Salad Tomatoes 6 Pack": 1,
        "Maris Piper Potatoes 2kg": 2,
        "Red Peppers 3 Pack": 3,
        "Chicken Breast Fillets 500g": 4,
    }
    for name, expected in cases.items():
        assert best_ingredient_type_id({"name": name, "category": []}, types) == expected


def test_unrelated_products_stay_unclassified():
    types = [(1, "Tomato"), (2, "Pepper")]
    for name in ["Peppercorn Sauce", "Chocolate Biscuits"]:
        assert best_ingredient_type_id({"name": name, "category": []}, types) is None
