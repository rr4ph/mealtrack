import hashlib
import hmac
import os
import secrets
import time

SECRET = os.environ.get("MEALTRACK_SECRET") or secrets.token_hex(32)
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7


def _sign(payload):
    return hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


def create_token(user_id):
    payload = f"{user_id}.{int(time.time()) + TOKEN_TTL_SECONDS}"
    return f"{payload}.{_sign(payload)}"


def verify_token(token):
    try:
        user_id, expires, signature = token.split(".")
        if not hmac.compare_digest(signature, _sign(f"{user_id}.{expires}")):
            return None
        if int(expires) < time.time():
            return None
        return int(user_id)
    except ValueError:
        return None


from fastapi import Depends, Header, HTTPException  # noqa: E402

from backend.database.connections import get_connection  # noqa: E402


def current_user_id(authorization: str | None = Header(default=None)):
    token = authorization.removeprefix("Bearer ") if authorization else ""
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return user_id


def require_query_user(user_id: int, auth_id: int = Depends(current_user_id)):
    if user_id != auth_id:
        raise HTTPException(status_code=403, detail="Forbidden.")


def _owner(query, value):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (value,))
            row = cursor.fetchone()
    return row[0] if row else None


def require_meal_owner(meal_id: int, auth_id: int = Depends(current_user_id)):
    if _owner("SELECT user_id FROM meals WHERE meal_id = %s", meal_id) != auth_id:
        raise HTTPException(status_code=404, detail="Meal not found.")


def require_inventory_owner(inventory_id: int, auth_id: int = Depends(current_user_id)):
    owner = _owner("SELECT user_id FROM user_inventories WHERE inventory_id = %s", inventory_id)
    if owner != auth_id:
        raise HTTPException(status_code=404, detail="Inventory not found.")
