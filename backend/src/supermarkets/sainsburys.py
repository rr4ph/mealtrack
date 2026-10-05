from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json

from backend.src.classes.product import Product
from backend.src.classes.shop import Shop
from backend.src.supermarkets.client import SupermarketClient
from backend.src.utils.enums import SupermarketType
from backend.src.utils.geography import get_coordinates


class Sainsburys(SupermarketClient):
    
    
    product_url = (
        "https://www.sainsburys.co.uk/"
        "groceries-api/gol-services/product/v1/product"
    )

    store_url = "https://stores.sainsburys.co.uk/api/v1/stores/"

    def get_product(self, query):
        params = urlencode({
            "filter[keyword]": query.lower().strip()
        })

        request = Request(
            self.product_url + "?" + params,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Language": "en-GB,en;q=0.9",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Version/26.6.2 Safari/605.1.15"
                ),
                "Referer": "https://www.sainsburys.co.uk/gol-ui/groceries",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
            }
        )

        response = urlopen(request)

        response = urlopen(request)

        data = json.load(response)
        return self.convert_product(data)

    def convert_product(self, data):
        products = []

        for product in data["products"]:
            products.append(
                Product(
                    external_id=product["product_uid"],
                    name=product["name"],
                    price=product["retail_price"]["price"],
                    currency="GBP",
                    unit_price=product["unit_price"]["price"],
                    unit_currency="GBP",
                    unit_name=product["unit_price"]["measure"],
                    promotions=[
                        promotion["strap_line"]
                        for promotion in product.get("promotions", [])
                    ],
                    category=[
                        category["name"]
                        for category in product.get("categories", [])
                    ],
                    supermarket=SupermarketType.SAINSBURYS
                )
            )

        return products

    def get_shops(self, postcode):
        latitude, longitude = get_coordinates(postcode)
        params = urlencode({
            "fields": "slfe-list-2.21",
            "api_client_id": "slfe",
            "lat": latitude,
            "lon": longitude,
            "limit": 25,
            "store_type": "main,local",
            "sort": "by_distance",
            "within": 15,
            "page": 1
        })

        response = urlopen(
            self.store_url + "?" + params
        )

        data = json.load(response)
        return self.convert_shops(data)

    def convert_shops(self, data):
        shops = []

        for shop in data["results"]:
            contact = shop["contact"]

            shop_address = ", ".join(
                part
                for part in [
                    contact["address1"],
                    contact["address2"],
                    contact["city"]
                ]
                if part
            )

            shops.append(
                Shop(
                    address_id=shop["code"],
                    shop_address=shop_address,
                    shop_name=shop["name"],
                    latitude=float(shop["location"]["lat"]),
                    longitude=float(shop["location"]["lon"]),
                    postal_code=contact["post_code"],
                    distance=shop["distance"]
                )
            )

        return shops