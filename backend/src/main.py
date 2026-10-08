import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.src.api.users import router as users_router
from backend.src.api.auth import router as auth_router
from backend.src.api.products import router as products_router
from backend.src.api.inventory import router as inventory_router
from backend.src.api.meals import router as meals_router
from backend.src.api.ingredients import router as ingredients_router
from backend.src.api.ingredient_types import router as ingredient_types_router
from backend.src.api.shortages import router as shortages_router
from backend.src.api.shops import router as shops_router
from backend.src.api.tracking import router as tracking_router

app = FastAPI()

# Get allowed origins from environment, fallback to localhost for development
allowed_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")
app.include_router(meals_router, prefix="/api")
app.include_router(ingredients_router, prefix="/api")
app.include_router(ingredient_types_router, prefix="/api")
app.include_router(shortages_router, prefix="/api")
app.include_router(shops_router, prefix="/api")
app.include_router(tracking_router, prefix="/api")
