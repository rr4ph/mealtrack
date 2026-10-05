from io import BytesIO
import json

from backend.src.supermarkets import morrisons
from backend.src.utils.enums import SupermarketType


def test_convert_product():
    data = {
        "productGroups": [
            {
                "decoratedProducts": [
                    {
                        "productId": "123",
                        "name": "Tomatoes",
                        "brand": "Test Brand",
                        "packSizeDescription": "500g",
                        "price": {"amount": 1.50, "currency": "GBP"},
                        "unitPrice": {
                            "price": {"amount": 3.00, "currency": "GBP"},
                            "unitName": "kg",
                        },
                        "isInCurrentCatalog": True,
                        "promotions": [{"description": "Save 20p"}],
                        "categoryPath": ["Fruit & Veg", "Tomatoes"],
                    }
                ]
            }
        ]
    }

    products = morrisons.Morrisons().convert_product(data)

    assert len(products) == 1
    product = products[0]
    assert product.external_id == "123"
    assert product.name == "Tomatoes"
    assert product.brand == "Test Brand"
    assert product.pack_size == "500g"
    assert product.price == 1.50
    assert product.currency == "GBP"
    assert product.promotions == ["Save 20p"]
    assert product.category == ["Fruit & Veg", "Tomatoes"]
    assert product.supermarket == SupermarketType.MORRISONS


def test_convert_product_without_promotions():
    data = {
        "productGroups": [
            {
                "decoratedProducts": [
                    {
                        "productId": "123",
                        "name": "Tomatoes",
                        "brand": "Test",
                        "price": {"amount": 1, "currency": "GBP"},
                        "unitPrice": {
                            "price": {"amount": 2, "currency": "GBP"},
                            "unitName": "kg",
                        },
                        "isInCurrentCatalog": True,
                        "categoryPath": [],
                    }
                ]
            }
        ]
    }

    products = morrisons.Morrisons().convert_product(data)

    assert products[0].promotions == []


def test_get_product_uses_normalised_query(monkeypatch):
    payload = {"productGroups": []}
    captured = {}

    def fake_urlopen(url):
        captured["url"] = url
        return BytesIO(json.dumps(payload).encode())

    monkeypatch.setattr(morrisons, "urlopen", fake_urlopen)

    assert morrisons.Morrisons().get_product("  TOMATOES  ") == []
    assert "q=tomatoes" in captured["url"]


def test_convert_shops():
    data = [
        {
            "addressId": "1",
            "formattedAddress": "123 High Street",
            "name": "Morrisons Glasgow",
            "coordinates": {"latitude": 55.86, "longitude": -4.25},
            "postalCode": "G1 1AA",
        }
    ]

    shops = morrisons.Morrisons().convert_shops(data)

    assert len(shops) == 1
    assert shops[0].address_id == "1"
    assert shops[0].shop_name == "Morrisons Glasgow"
    assert shops[0].distance is None


def test_get_shops(monkeypatch):
    payload = []
    captured = {}

    def fake_urlopen(url):
        captured["url"] = url
        return BytesIO(json.dumps(payload).encode())

    monkeypatch.setattr(morrisons, "urlopen", fake_urlopen)

    assert morrisons.Morrisons().get_shops("G1 1AA") == []
    assert "CUSTOMER_COLLECTION" in captured["url"]
