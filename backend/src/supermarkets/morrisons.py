from urllib.request import urlopen
import json
from backend.src.classes.product import Product
from backend.src.classes.shop import Shop
from backend.src.supermarkets.client import SupermarketClient
from backend.src.utils.enums import SupermarketType

class Morrisons(SupermarketClient):

    base_url = "https://groceries.morrisons.com"    
    
    def get_product(self, query):
        response = urlopen(
            self.base_url +
            "/api/webproductpagews/v6/product-pages/search"
            "?includeAdditionalPageInfo=true"
            "&maxPageSize=300"
            "&maxProductsToDecorate=50"
            "&q="
            + query.lower().strip() 
            + "&tag=web"
        )
        
        data = json.load(response)
        return self.convert_product(data)

    def convert_product(self, data):
        products = []

        for group in data["productGroups"]:
            for product in group["decoratedProducts"]:
                products.append(
                    Product(
                        external_id=product["productId"],
                        name=product["name"],
                        brand=product["brand"],
                        pack_size=product.get("packSizeDescription"),
                        price=product["price"]["amount"],
                        currency=product["price"]["currency"],
                        unit_price=product["unitPrice"]["price"]["amount"],
                        unit_currency=product["unitPrice"]["price"]["currency"],
                        unit_name=product["unitPrice"]["unitName"],
                        in_catalog=product["isInCurrentCatalog"],
                        promotions=[
                            promo["description"]
                            for promo in product.get("promotions", [])
                        ],
                        category=product["categoryPath"],
                        supermarket=SupermarketType.MORRISONS
                    )
                )

        return products

    def get_shops(self, location=None):
        response = urlopen(
            self.base_url +
            "/api/ecomdeliverydestinations/v4/delivery-addresses"
            "?deliveryMethod=CUSTOMER_COLLECTION")
        
        data = json.load(response)
        return self.convert_shops(data)

    def convert_shops(self, data):
        shops = []

        for shop in data:
            shops.append(
                Shop(
                    address_id=shop["addressId"],
                    shop_address=shop["formattedAddress"],
                    shop_name=shop["name"],
                    latitude=shop["coordinates"]["latitude"],
                    longitude=shop["coordinates"]["longitude"],
                    postal_code=shop["postalCode"]
                )
            )

        return shops

    