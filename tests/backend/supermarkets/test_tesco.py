import pytest
from backend.src.supermarkets import tesco
from backend.src.utils.enums import SupermarketType


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


REEF_RESPONSE = {"ok": True, "data": {"results": [
    {
        "product_id": "abc",
        "title": "Milk 2.272L",
        "brand": "Tesco",
        "price": 1.50,
        "member_price": 1.00,
        "currency": "GBP",
        "unit_price": 0.66,
        "unit_of_measure": "litre",
        "breadcrumb": ["Dairy", "Milk"],
    },
    {"title": "No id", "price": 1},
]}}


def test_convert_product():
    products = tesco.Tesco().convert_product(REEF_RESPONSE)

    assert len(products) == 1
    product = products[0]
    assert product.external_id == "abc"
    assert product.name == "Milk 2.272L"
    assert product.brand == "Tesco"
    assert product.price == 1.50
    assert product.currency == "GBP"
    assert product.unit_price == 0.66
    assert product.unit_name == "litre"
    assert product.category == ["Dairy", "Milk"]
    assert product.in_catalog is False
    assert product.supermarket == SupermarketType.TESCO


def test_convert_product_optional_fields():
    data = {"data": {"results": [
        {"product_id": 7, "title": "Milk", "price": 1}
    ]}}

    product = tesco.Tesco().convert_product(data)[0]

    assert product.brand is None
    assert product.pack_size is None
    assert product.currency == "GBP"
    assert product.external_id == "7"


def test_get_product(monkeypatch):
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse({"ok": True, "data": {"results": []}})

    monkeypatch.setenv("REEF_API_KEY", "test-key")
    monkeypatch.setattr(tesco.requests, "post", fake_post)

    assert tesco.Tesco().get_product("milk") == []
    assert captured["url"] == "https://api.reefapi.com/tesco/v1/search"
    assert captured["headers"]["x-api-key"] == "test-key"
    assert captured["json"] == {"query": "milk", "country": "uk"}


def test_get_product_raises_for_http_error(monkeypatch):
    class ErrorResponse:
        def raise_for_status(self):
            raise RuntimeError("HTTP error")

    monkeypatch.setenv("REEF_API_KEY", "test-key")
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


def test_get_product_requires_api_key(monkeypatch):
    monkeypatch.delenv("REEF_API_KEY", raising=False)

    try:
        tesco.Tesco().get_product("milk")
    except RuntimeError as error:
        assert "REEF_API_KEY" in str(error)
    else:
        raise AssertionError("Expected missing key error")


def test_convert_shops():
    data = {"elements": [
        {
            "type": "way", "id": 5,
            "center": {"lat": 55.86, "lon": -4.25},
            "tags": {
                "name": "Tesco Extra", "addr:housenumber": "1",
                "addr:street": "Main Street", "addr:city": "Glasgow",
                "addr:postcode": "G1 1AA",
            },
        },
        {"type": "node", "id": 6, "lat": 55.0, "lon": -4.0, "tags": {}},
        {"type": "way", "id": 7, "tags": {"name": "No coords"}},
    ]}

    shops = tesco.Tesco().convert_shops(data)

    assert len(shops) == 2
    assert shops[0].address_id == "way/5"
    assert shops[0].shop_address == "1 Main Street, Glasgow"
    assert shops[0].postal_code == "G1 1AA"
    assert (shops[0].latitude, shops[0].longitude) == (55.86, -4.25)
    assert shops[0].distance is None
    assert shops[1].shop_name == "Tesco"


def test_convert_shops_malformed():
    assert tesco.Tesco().convert_shops({}) == []
    assert tesco.Tesco().convert_shops({"elements": [{"type": "node"}]}) == []


@pytest.fixture(autouse=True)
def clear_shops_cache():
    tesco.Tesco._shops_cache.clear()


def test_get_shops_uses_cache_after_success(monkeypatch):
    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        return FakeResponse({"elements": []})

    monkeypatch.setattr(tesco, "get_coordinates", lambda postcode: (55.86, -4.25))
    monkeypatch.setattr(tesco.requests, "post", fake_post)

    tesco.Tesco().get_shops("G1 1AA")
    tesco.Tesco().get_shops("G1 1AA")

    assert len(calls) == 1


def test_get_shops(monkeypatch):
    captured = {}

    def fake_post(url, data, headers, timeout):
        captured["url"] = url
        captured["query"] = data["data"]
        return FakeResponse({"elements": []})

    monkeypatch.setattr(tesco, "get_coordinates", lambda postcode: (55.86, -4.25))
    monkeypatch.setattr(tesco.requests, "post", fake_post)

    assert tesco.Tesco().get_shops("G1 1AA") == []
    assert captured["url"] == tesco.Tesco.overpass_urls[0]
    assert "55.86,-4.25" in captured["query"]


def test_get_shops_falls_back_to_second_mirror(monkeypatch):
    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            raise tesco.requests.ConnectionError("busy")
        return FakeResponse({"elements": []})

    monkeypatch.setattr(tesco, "get_coordinates", lambda postcode: (55.86, -4.25))
    monkeypatch.setattr(tesco.requests, "post", fake_post)

    assert tesco.Tesco().get_shops("G1 1AA") == []
    assert calls == tesco.Tesco.overpass_urls


def test_get_shops_retries_mirrors_before_giving_up(monkeypatch):
    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        if len(calls) <= len(tesco.Tesco.overpass_urls):
            raise tesco.requests.ConnectionError("busy")
        return FakeResponse({"elements": []})

    monkeypatch.setattr(tesco, "get_coordinates", lambda postcode: (55.86, -4.25))
    monkeypatch.setattr(tesco.requests, "post", fake_post)

    assert tesco.Tesco().get_shops("G1 1AA") == []
    assert calls == tesco.Tesco.overpass_urls + tesco.Tesco.overpass_urls[:1]


def test_get_shops_raises_for_http_error(monkeypatch):
    class Bad(FakeResponse):
        def raise_for_status(self):
            raise tesco.requests.HTTPError("HTTP error")

    monkeypatch.setattr(tesco, "get_coordinates", lambda postcode: (55.86, -4.25))
    monkeypatch.setattr(tesco.requests, "post", lambda *a, **k: Bad({}))

    try:
        tesco.Tesco().get_shops("G1 1AA")
    except tesco.requests.HTTPError as error:
        assert str(error) == "HTTP error"
    else:
        raise AssertionError("Expected HTTP error")
