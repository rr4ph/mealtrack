from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.src.classes.user import User

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    postcode: str | None = None

@router.post("/users")
def create_user(user_data: UserCreate):
    user = User(
        username=user_data.username,
        password=user_data.password
    )

    user.postcode = user_data.postcode

    try:
        user.save_user()
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "user_id": user.user_id,
        "username": user.username,
        "postcode": user.postcode,
        "inventory_id": user.inventory.inventory_id
    }