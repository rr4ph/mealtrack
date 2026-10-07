from difflib import SequenceMatcher

from backend.src.utils.association_algorithms import association_score

MATCH_THRESHOLD = 0.6
TOKEN_SIMILARITY = 0.85


def _stem(word):
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith(("oes", "ses", "xes", "ches", "shes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _normalise(text):
    return " ".join(_stem(word) for word in text.lower().split())


def best_ingredient_type_id(product, ingredient_types, threshold=MATCH_THRESHOLD):
    """Return the id of the best-scoring ingredient type, or None if not confident.

    Words are stemmed so plurals match (tomato/tomatoes). A type only qualifies
    if every word of its name closely matches a word in the product name.
    """
    product = {
        "name": _normalise(product["name"]),
        "category": [_normalise(c) for c in product.get("category") or []],
    }
    product_words = product["name"].split()
    best_id = None
    best_score = 0

    for ingredient_type_id, name in ingredient_types:
        candidate = {"name": _normalise(name)}
        words = candidate["name"].split()
        if not words or not all(
            any(SequenceMatcher(None, w, p).ratio() >= TOKEN_SIMILARITY for p in product_words)
            for w in words
        ):
            continue
        score = association_score(product, candidate)
        if score >= threshold and score > best_score:
            best_id, best_score = ingredient_type_id, score

    return best_id
