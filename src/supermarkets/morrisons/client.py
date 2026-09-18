from urllib.request import urlopen
import json

class Morrisons:

    base_url = "https://groceries.morrisons.com"
    userAddress = {
        "address": "30 Washington Street, Glasgow, G38AZ, United Kingdom",
        "latitude": 55.858215,
        "longitude": -4.269189
    }
    
    
    def get_product(self, query):
        response = urlopen(
            self.base_url 
            + "/api/webproductpagews/v6/product-pages/search?includeAdditionalPageInfo=true&maxPageSize=300&maxProductsToDecorate=50&q=" 
            + query.lower().strip() 
            +"&tag=web")

        data = json.load(response)

        return self.convert_product(data)

    def convert_product(self, data):
        products = []

        for group in data["productGroups"]:
            for product in group["decoratedProducts"]:
                products.append({
                    "id": product["productId"],
                    "name": product["name"],
                    "brand": product["brand"],
                    "pack_size": product.get("packSizeDescription"),
                    "price": float(product["price"]["amount"]),
                    "currency": product["price"]["currency"],
                    "unitPrice": float(product["unitPrice"]["price"]["amount"]),
                    "unitCurrency": product["unitPrice"]["price"]["currency"],
                    "unitName": product["unitPrice"]["unitName"],
                    "inCatalog": product["isInCurrentCatalog"],
                    "promotions": [
                        promo["description"]
                        for promo in product.get("promotions", []) 
                    ],
                    "category": product["categoryPath"]
                })

        return products

    def get_shops(self):
        response = urlopen(self.base_url + "/api/ecomdeliverydestinations/v4/delivery-addresses?deliveryMethod=CUSTOMER_COLLECTION")
        data = json.load(response)

        return self.convert_shops(data)

    def convert_shops(self, data):
        shops = []

        for shop in data:
            shops.append({
                "addressId": shop["addressId"],
                "shopAddress": shop["formattedAddress"],
                "shopName": shop["name"],
                "coordinates": {
                    "latitude": shop["coordinates"]["latitude"],
                    "longitude": shop["coordinates"]["longitude"]
                },
                "postalCode": shop["postalCode"]
            })

        return shops