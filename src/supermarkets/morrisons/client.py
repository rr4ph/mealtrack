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

        return data

    def get_shops(self):
        response = urlopen(self.base_url + "/api/ecomdeliverydestinations/v4/delivery-addresses?deliveryMethod=CUSTOMER_COLLECTION")
        data = json.load(response)

        return data