from backend.src.supermarkets import tesco
from backend.src.utils.enums import SupermarketType


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


def test_convert_product():
    data = [{
        "data": {
            "search": {
                "results": [
                    {
                        "node": {
                            "__typename": "ProductType",
                            "id": "abc",
                            "title": "Milk",
                            "brandName": "Tesco",
                            "price": {
                                "actual": 1.50,
                                "unitPrice": 1.50,
                                "unitOfMeasure": "litre",
                            },
                            "promotions": [{"description": "Clubcard Price"}],
                            "departmentName": "Milk & Dairy",
                        }
                    },
                    {
                        "node": {
                            "__typename": "OtherType",
                            "id": "ignored",
                        }
                    },
                ]
            }
        }
    }]

    products = tesco.Tesco().convert_product(data)

    assert len(products) == 1
    product = products[0]
    assert product.external_id == "abc"
    assert product.name == "Milk"
    assert product.brand == "Tesco"
    assert product.price == 1.50
    assert product.currency == "GBP"
    assert product.promotions == ["Clubcard Price"]
    assert product.category == "Milk & Dairy"
    assert product.supermarket == SupermarketType.TESCO


def test_convert_product_optional_fields():
    data = [{
        "data": {
            "search": {
                "results": [
                    {
                        "node": {
                            "__typename": "ProductType",
                            "id": "abc",
                            "title": "Milk",
                            "price": {
                                "actual": 1,
                                "unitPrice": 1,
                                "unitOfMeasure": "litre",
                            },
                        }
                    }
                ]
            }
        }
    }]

    product = tesco.Tesco().convert_product(data)[0]

    assert product.brand is None
    assert product.promotions == []
    assert product.category is None


def test_get_product(monkeypatch):
    captured = {}

    def fake_post(url, headers, json):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse([{
            "data": {
                "search": {
                    "results": []
                }
            }
        }])

    monkeypatch.setenv("TESCO_API_KEY", "test-key")
    monkeypatch.setattr(tesco.requests, "post", fake_post)

    assert tesco.Tesco().get_product("milk") == []
    assert captured["url"] == tesco.Tesco.base_url
    assert captured["headers"]["x-apikey"] == "test-key"
    assert captured["json"][0]["variables"]["query"] == "milk"


def test_get_product_raises_for_http_error(monkeypatch):
    class ErrorResponse:
        def raise_for_status(self):
            raise RuntimeError("HTTP error")

    monkeypatch.setenv("TESCO_API_KEY", "test-key")
    monkeypatch.setattr(
        tesco.requests,
        "post",
        lambda *args, **kwargs: ErrorResponse(),
    )

    try:
        tesco.Tesco().get_product("milk")
    except RuntimeError as error:
        assert str(error) == "HTTP error"
    else:
        raise AssertionError("Expected HTTP error")


def test_convert_shops():
    data = [
        {
            "profile": {
                "meta": {"id": "1"},
                "name": "Tesco Glasgow",
                "address": {
                    "line1": "1 Main Street",
                    "line2": "",
                    "line3": None,
                    "city": "Glasgow",
                    "postalCode": "G1 1AA",
                },
                "yextRoutableCoordinate": {
                    "lat": 55.86,
                    "long": -4.25,
                },
            },
            "distance": {"distanceKilometers": 2.5},
        }
    ]

    shops = tesco.Tesco().convert_shops(data)

    assert len(shops) == 1
    assert shops[0].address_id == "1"
    assert shops[0].shop_address == "1 Main Street, Glasgow"
    assert shops[0].distance == 2.5


def test_get_shops(monkeypatch):
    captured = {}

    def fake_get(url, params):
        captured["url"] = url
        captured["params"] = params
        return FakeResponse([])

    monkeypatch.setattr(tesco.requests, "get", fake_get)

    assert tesco.Tesco().get_shops("G1 1AA") == []
    assert captured["url"] == tesco.Tesco.store_locator_url
    assert captured["params"]["q"] == "G1 1AA"
