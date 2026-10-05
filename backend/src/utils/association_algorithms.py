from difflib import SequenceMatcher

def exact_match(product, ingredient_type):
    product_tags = product["name"].lower().split()
    ingredient_tags = ingredient_type["name"].lower().split()
    matches = 0

    for ingredient_tag in ingredient_tags:
        if ingredient_tag in product_tags:
            matches += 1

    return matches / len(ingredient_tags)

def fuzzy_match(product, ingredient_type):
    product_tags = product["name"].lower().split()
    ingredient_tags = ingredient_type["name"].lower().split()
    scores = []

    for ingredient_tag in ingredient_tags:
        best_score = 0

        for product_tag in product_tags:
            score = SequenceMatcher(
                None, 
                ingredient_tag, 
                product_tag
                ).ratio()

            if score > best_score:
                best_score = score

        scores.append(best_score)

    return sum(scores) / len(scores)

def category_match(product, ingredient_type):
    ingredient_tags = ingredient_type["name"].lower().split()
    category = product.get("category", [])
    category_tags = []

    for category_tag in category:
        category_tags.append(category_tag.lower().split())

    matches = 0

    for ingredient_tag in ingredient_tags:
        for category_tag in category_tags:
            if ingredient_tag in category_tag:
                matches += 1
                break

    return matches / len(ingredient_tags)



def association_score(product, ingredient_type, user_review=False):
    exact = exact_match(product, ingredient_type)
    fuzzy = fuzzy_match(product, ingredient_type)
    category = category_match(product, ingredient_type)

    return (
        exact * 0.4 
        + fuzzy * 0.25
        + category * 0.3
    ) 
