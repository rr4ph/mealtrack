import pytest

from backend.src.utils.association_algorithms import (
    association_score,
    category_match,
    exact_match,
    fuzzy_match,
)


def test_exact_match():
    product = {"name": "British Tomatoes 500g"}
    ingredient = {"name": "Tomatoes"}

    assert exact_match(product, ingredient) == 1.0


def test_exact_match_partial():
    product = {"name": "British Tomato Soup"}
    ingredient = {"name": "Tomato Sauce"}

    assert exact_match(product, ingredient) == 0.5


def test_exact_match_case_insensitive():
    product = {"name": "Fresh MILK"}
    ingredient = {"name": "milk"}

    assert exact_match(product, ingredient) == 1.0


def test_fuzzy_match_exact_is_one():
    product = {"name": "tomato"}
    ingredient = {"name": "tomato"}

    assert fuzzy_match(product, ingredient) == 1.0


def test_fuzzy_match_close_word_scores_above_zero():
    product = {"name": "tomatoes"}
    ingredient = {"name": "tomato"}

    assert 0 < fuzzy_match(product, ingredient) < 1


def test_category_match():
    product = {
        "name": "Passata",
        "category": ["Food", "Tomato Products"],
    }
    ingredient = {"name": "Tomato"}

    assert category_match(product, ingredient) == 1.0


def test_category_match_no_category():
    product = {"name": "Pizza"}
    ingredient = {"name": "Tomato"}

    assert category_match(product, ingredient) == 0.0


def test_association_score_combines_three_signals():
    product = {
        "name": "Tomato",
        "category": ["Tomato Products"],
    }
    ingredient = {"name": "Tomato"}

    # Weights: exact=0.25, fuzzy=0.15, category=0.6
    # All three signals match perfectly
    expected = 0.25 + 0.15 + 0.6

    assert association_score(product, ingredient) == pytest.approx(expected)
