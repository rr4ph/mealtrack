from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.src.utils.ingredient_type_methods import (
    create_ingredient_type as create_ingredient_type_db,
    merge_ingredient_types as merge_ingredient_types_db
)

router = APIRouter()


class IngredientTypeCreate(BaseModel):
    name: str


class IngredientTypeMerge(BaseModel):
    kept_id: int
    deleted_id: int


@router.post("/ingredient-types")
def create_ingredient_type(type_data: IngredientTypeCreate):
    try:
        create_ingredient_type_db(type_data.name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"message": "Ingredient type created successfully."}


@router.post("/ingredient-types/merge")
def merge_ingredient_types(merge_data: IngredientTypeMerge):
    if merge_data.kept_id == merge_data.deleted_id:
        raise HTTPException(
            status_code=400,
            detail="Kept and deleted ingredient types must be different."
        )

    try:
        merge_ingredient_types_db(
            merge_data.kept_id,
            merge_data.deleted_id
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"message": "Ingredient types merged successfully."}