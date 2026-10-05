from io import BytesIO
import json

import pytest

from backend.src.classes.shop import Shop
from backend.src.utils import geography


def test_haversine_same_point():
    assert geography.haversine(55.0, -4.0, 55.0, -4.0) == 0


def test_haversine_known_distance():
    distance = geography.haversine(0, 0, 0, 1)

    assert distance == pytest.approx(111.195, rel=1e-3)


def test_get_shop_distances_sorts_shops():
    shops = [
        Shop("2", "far", "Far", 0, 2, "FAR"),
        Shop("1", "near", "Near", 0, 1, "NEAR"),
    ]

    result = geography.get_shop_distances(shops, 0, 0)

    assert result[0].shop_name == "Near"
    assert result[1].shop_name == "Far"
    assert result[0].distance == pytest.approx(111.19, abs=0.01)


def test_get_coordinates(monkeypatch):
    payload = {
        "result": {
            "latitude": 55.8642,
            "longitude": -4.2518,
        }
    }

    monkeypatch.setattr(
        geography,
        "urlopen",
        lambda url: BytesIO(json.dumps(payload).encode()),
    )

    assert geography.get_coordinates(" G1 1AA ") == (
        55.8642,
        -4.2518,
    )


def test_get_coordinates_invalid_response(monkeypatch):
    monkeypatch.setattr(
        geography,
        "urlopen",
        lambda url: BytesIO(b'{"result": null}'),
    )

    with pytest.raises(ValueError, match="Coordinates for postcode"):
        geography.get_coordinates("INVALID")
