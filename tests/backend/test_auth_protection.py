import pytest
from fastapi import HTTPException

from backend.src.utils.auth import create_token, current_user_id, require_query_user
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)


def test_current_user_id_accepts_valid_token():
    assert current_user_id(f"Bearer {create_token(7)}") == 7


def test_current_user_id_rejects_missing_or_bad_token():
    for header in (None, "Bearer nope", f"Bearer {create_token(7)}x"):
        with pytest.raises(HTTPException) as exc:
            current_user_id(header)
        assert exc.value.status_code == 401


def test_query_user_must_match_token_user():
    require_query_user(3, 3)
    with pytest.raises(HTTPException) as exc:
        require_query_user(4, 3)
    assert exc.value.status_code == 403


def test_protected_routes_require_token():
    assert client.get("/api/meals?user_id=1").status_code == 401
    assert client.get("/api/inventory?user_id=1").status_code == 401
    assert client.post("/api/inventory/1/items", json={"product_id": 1, "quantity": 1, "quantity_unit": "g"}).status_code == 401
    assert client.delete("/api/meals/1/ingredients/1").status_code == 401


def test_cannot_read_other_users_meals():
    headers = {"Authorization": f"Bearer {create_token(1)}"}
    assert client.get("/api/meals?user_id=2", headers=headers).status_code == 403
