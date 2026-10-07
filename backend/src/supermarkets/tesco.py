import datetime
import os
import time
import requests
from backend.src.classes.product import Product
from backend.src.classes.shop import Shop
from backend.src.supermarkets.client import SupermarketClient
from backend.src.utils.enums import SupermarketType
from backend.src.utils.geography import get_coordinates


class Tesco(SupermarketClient):

    base_url = "https://api.reefapi.com"
    search_path = "/tesco/v1/search"
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]
    shop_radius_m = 15000
    overpass_attempts = 4
    shops_cache_seconds = 24 * 60 * 60
    _shops_cache = {}

    def get_product(self, query):
        api_key = os.environ.get("REEF_API_KEY")
        if not api_key:
            raise RuntimeError("REEF_API_KEY is not set")

        response = requests.post(
            self.base_url + self.search_path,
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={"query": query, "country": "uk"},
            timeout=30
        )

        response.raise_for_status()

        return self.convert_product(response.json())

    def convert_product(self, data):
        items = (data.get("data") or {}).get("results") or []

        products = []

        for item in items:
            external_id = item.get("product_id")
            if external_id is None or item.get("price") is None:
                continue

            currency = item.get("currency") or "GBP"
            products.append(
                Product(
                    external_id=str(external_id),
                    name=item["title"],
                    brand=item.get("brand"),
                    price=item["price"],
                    currency=currency,
                    unit_price=item.get("unit_price"),
                    unit_currency=currency,
                    unit_name=item.get("unit_of_measure"),
                    category=item.get("breadcrumb"),
                    supermarket=SupermarketType.TESCO,
                    last_price_update_at=datetime.datetime.now()
                )
            )

        return products

    def get_shops(self, postcode):
        latitude, longitude = get_coordinates(postcode)
        cache_key = (round(latitude, 3), round(longitude, 3))
        cached = self._shops_cache.get(cache_key)
        if cached and time.time() - cached[0] < self.shops_cache_seconds:
            return self.convert_shops(cached[1])

        query = (
            "[out:json][timeout:25];"
            '(nwr["brand:wikidata"="Q487494"]["shop"~"^(supermarket|convenience)$"]'
            f"(around:{self.shop_radius_m},{latitude},{longitude}););"
            "out center tags;"
        )

        last_error = None
        response = None
        for url in self.overpass_urls * self.overpass_attempts:
            try:
                response = requests.post(
                    url,
                    data={"data": query},
                    headers={
                        "User-Agent": "Mealtrack/0.1 (personal project)",
                        "Accept": "application/json"
                    },
                    timeout=30
                )
                response.raise_for_status()
                break
            except requests.RequestException as error:
                last_error = error
        else:
            raise last_error

        data = response.json()
        self._shops_cache[cache_key] = (time.time(), data)

        return self.convert_shops(data)

    def convert_shops(self, data):
        shops = []

        for element in data.get("elements", []):
            tags = element.get("tags", {})
            point = element if "lat" in element else element.get("center", {})

            if "lat" not in point or "lon" not in point:
                continue

            shop_address = ", ".join(
                tags[key]
                for key in [
                    "addr:housenumber", "addr:street",
                    "addr:suburb", "addr:city"
                ]
                if tags.get(key)
            )
            if tags.get("addr:housenumber") and tags.get("addr:street"):
                shop_address = shop_address.replace(
                    f"{tags['addr:housenumber']}, ", f"{tags['addr:housenumber']} ", 1
                )

            shops.append(
                Shop(
                    address_id=f"{element['type']}/{element['id']}",
                    shop_address=shop_address,
                    shop_name=tags.get("name", "Tesco"),
                    latitude=point["lat"],
                    longitude=point["lon"],
                    postal_code=tags.get("addr:postcode", "")
                )
            )

        return shops


if __name__ == "__main__":
    products = Tesco().get_product("bread")

    for product in products:
        print(product.name, product.price)