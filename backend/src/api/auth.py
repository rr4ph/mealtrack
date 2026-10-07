from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from backend.database.connections import get_connection
from backend.src.utils.auth import create_token, current_user_id, verify_token

router = APIRouter()
phasher = PasswordHasher()


class LoginRequest(BaseModel):
    username: str
    password: str


class SessionResponse(BaseModel):
    user_id: int
    username: str
    postcode: str | None = None
    token: str


class MeResponse(BaseModel):
    user_id: int
    username: str
    postcode: str | None = None


@router.post("/auth/login", response_model=SessionResponse)
def login(data: LoginRequest):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, username, password_hash, postcode
                FROM users WHERE username = %s
                """,
                (data.username,)
            )
            rows = cursor.fetchall()

    for user_id, username, password_hash, postcode in rows:
        try:
            phasher.verify(password_hash, data.password)
        except VerificationError:
            continue
        return SessionResponse(
            user_id=user_id,
            username=username,
            postcode=postcode,
            token=create_token(user_id)
        )

    raise HTTPException(status_code=401, detail="Invalid username or password.")


@router.get("/auth/me", response_model=MeResponse)
def me(authorization: str | None = Header(default=None)):
    token = authorization.removeprefix("Bearer ") if authorization else ""
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT username, postcode FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    return MeResponse(user_id=user_id, username=row[0], postcode=row[1])


class AccountUpdate(BaseModel):
    username: str
    postcode: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.patch("/auth/account", response_model=MeResponse)
def update_account(data: AccountUpdate, user_id: int = Depends(current_user_id)):
    username = data.username.strip()
    postcode = (data.postcode or "").strip() or None
    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM users WHERE username = %s AND user_id <> %s",
                (username, user_id)
            )
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="That username is already taken.")
            cursor.execute(
                "UPDATE users SET username = %s, postcode = %s WHERE user_id = %s",
                (username, postcode, user_id)
            )

    return MeResponse(user_id=user_id, username=username, postcode=postcode)


@router.post("/auth/password", response_model=SessionResponse)
def change_password(data: PasswordChange, user_id: int = Depends(current_user_id)):
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters.")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT username, password_hash, postcode FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(status_code=401, detail="Invalid or expired session.")
            try:
                phasher.verify(row[1], data.current_password)
            except VerificationError:
                raise HTTPException(status_code=400, detail="Current password is incorrect.")
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE user_id = %s",
                (phasher.hash(data.new_password), user_id)
            )

    return SessionResponse(
        user_id=user_id, username=row[0], postcode=row[2], token=create_token(user_id)
    )
