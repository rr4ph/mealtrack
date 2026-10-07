from io import BytesIO
import json

from backend.src.supermarkets import sainsburys
from backend.src.utils.enums import SupermarketType


def test_convert_product():
    data = {
        "products": [
            {
                "product_uid": "s123",
                "name": "Tomatoes",
                "retail_price": {"price": 1.50},
                "unit_price": {"price": 3.00, "measure": "kg"},
                "promotions": [{"strap_line": "Save 30p"}],
                "categories": [
                    {"name": "Fruit & Veg"},
                    {"name": "Tomatoes"},
                ],
            }
        ]
    }

    product = sainsburys.Sainsburys().convert_product(data)[0]

    assert product.external_id == "s123"
    assert product.name == "Tomatoes"
    assert product.price == 1.50
    assert product.currency == "GBP"
    assert product.unit_price == 3.00
    assert product.unit_name == "kg"
    assert product.promotions == ["Save 30p"]
    assert product.category == ["Fruit & Veg", "Tomatoes"]
    assert product.supermarket == SupermarketType.SAINSBURYS


def test_convert_product_without_optional_fields():
    data = {
        "products": [
            {
                "product_uid": "s123",
                "name": "Tomatoes",
                "retail_price": {"price": 1},
                "unit_price": {"price": 2, "measure": "kg"},
            }
        ]
    }

    product = sainsburys.Sainsburys().convert_product(data)[0]

    assert product.promotions == []
    assert product.category == []


def test_get_product_normalises_query(monkeypatch):
    captured = {}

    def fake_urlopen(request):
        captured["url"] = request.full_url
        captured["calls"] = captured.get("calls", 0) + 1
        return BytesIO(b'{"products": []}')

    monkeypatch.setattr(sainsburys, "urlopen", fake_urlopen)

    assert sainsburys.Sainsburys().get_product("  TOMATOES  ") == []
    assert "filter%5Bkeyword%5D=tomatoes" in captured["url"]
    assert captured["calls"] == 1


def test_convert_shops():
    data = {
        "results": [
            {
                "code": "s1",
                "name": "Sainsbury's Glasgow",
                "contact": {
                    "address1": "1 Main Street",
                    "address2": "",
                    "city": "Glasgow",
                    "post_code": "G1 1AA",
                },
                "location": {
                    "lat": "55.86",
                    "lon": "-4.25",
                },
                "distance": 1.7,
            }
        ]
    }

    shop = sainsburys.Sainsburys().convert_shops(data)[0]

    assert shop.address_id == "s1"
    assert shop.shop_name == "Sainsbury's Glasgow"
    assert shop.shop_address == "1 Main Street, Glasgow"
    assert shop.latitude == 55.86
    assert shop.longitude == -4.25
    assert shop.distance == 1.7


def test_get_shops_uses_postcode_coordinates(monkeypatch):
    captured = {}

    monkeypatch.setattr(
        sainsburys,
        "get_coordinates",
        lambda postcode: (55.86, -4.25),
    )

    def fake_urlopen(url):
        captured["url"] = url
        return BytesIO(b'{"results": []}')

    monkeypatch.setattr(sainsburys, "urlopen", fake_urlopen)

    assert sainsburys.Sainsburys().get_shops("G1 1AA") == []
    assert "lat=55.86" in captured["url"]
    assert "lon=-4.25" in captured["url"]
