from  fastapi import FastAPI
from src.supermarkets.morrisons.client import Morrisons

app = FastAPI()

@app.get("/api/products")
def get_products(query: str):
    morrisons = Morrisons()
    return morrisons.get_product(query)