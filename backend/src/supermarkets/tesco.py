import os
import requests
from backend.src.classes.product import Product
from backend.src.classes.shop import Shop
from backend.src.supermarkets.client import SupermarketClient
from backend.src.utils.enums import SupermarketType


class Tesco(SupermarketClient):

    base_url = "https://xapi.tesco.com/"
    store_locator_url = "https://www.tesco.com/store-locator/searchapi"

    search_query = """
        query Search(
            $query: String!,
            $page: Int = 1,
            $sortBy: String,
            $journey: SearchJourneyType,
            $primarySearchMode: SearchModeType
        ) {
            search(
                query: $query
                journey: $journey
                mode: $primarySearchMode
                page: $page
                sortBy: $sortBy
            ) {
                results {
                    node {
                        __typename
                        ... on ProductType {
                            id
                            title
                            brandName
                            price {
                                actual
                                unitPrice
                                unitOfMeasure
                            }
                            promotions {
                                description
                            }
                            departmentName
                        }
                    }
                }
            }
        }
    """

    def get_product(self, query):
        payload = [{
            "operationName": "Search",
            "variables": {
                "page": 1,
                "query": query,
                "sortBy": "relevance",
                "journey": "ONLINE",
                "primarySearchMode": "DEFAULT"
            },
            "extensions": {
                "mfeName": "mfe-plp"
            },
            "query": self.search_query
        }]

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "en-GB",
            "Origin": "https://www.tesco.com",
            "Referer": (
                "https://www.tesco.com/shop/en-GB/search"
                f"?query={query}&inputType=free+text"
            ),
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/26.6.2 Safari/605.1.15"
            ),
            "x-apikey": os.environ["TESCO_API_KEY"],
            "region": "UK",
            "language": "en-GB"
        }

        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload
        )

        response.raise_for_status()

        return self.convert_product(response.json())

    def convert_product(self, data):
        products = []

        for result in data[0]["data"]["search"]["results"]:
            product = result["node"]

            if product["__typename"] != "ProductType":
                continue

            products.append(
                Product(
                    external_id=product["id"],
                    name=product["title"],
                    brand=product.get("brandName"),
                    price=product["price"]["actual"],
                    currency="GBP",
                    unit_price=product["price"]["unitPrice"],
                    unit_currency="GBP",
                    unit_name=product["price"]["unitOfMeasure"],
                    promotions=[
                        promotion["description"]
                        for promotion in product.get("promotions", [])
                    ],
                    category=product.get("departmentName"),
                    supermarket=SupermarketType.TESCO
                )
            )

        return products

    def get_shops(self, postcode):
        response = requests.get(
            self.store_locator_url,
            params={
                "q": postcode,
                "qp": postcode,
                "l": "en"
            }
        )

        response.raise_for_status()

        return self.convert_shops(response.json())

    def convert_shops(self, data):
        shops = []

        for shop in data:
            profile = shop["profile"]
            address = profile["address"]

            shop_address = ", ".join(
                part
                for part in [
                    address["line1"],
                    address["line2"],
                    address["line3"],
                    address["city"]
                ]
                if part
            )

            shops.append(
                Shop(
                    address_id=profile["meta"]["id"],
                    shop_address=shop_address,
                    shop_name=profile["name"],
                    latitude=profile["yextRoutableCoordinate"]["lat"],
                    longitude=profile["yextRoutableCoordinate"]["long"],
                    postal_code=address["postalCode"],
                    distance=shop["distance"]["distanceKilometers"]
                )
            )

        return shops


if __name__ == "__main__":
    products = Tesco().get_product("bread")

    for product in products:
        print(product.name, product.price)