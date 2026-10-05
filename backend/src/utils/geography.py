from math import radians, sin, cos, sqrt, atan2
from urllib.request import urlopen
import json
from urllib.error import HTTPError, URLError

def haversine(lat1, lon1, lat2, lon2):

    R = 6371

    delta_lat = radians(lat2 - lat1)

    delta_lon = radians(lon2 - lon1)

    lat1 = radians(lat1)

    lat2 = radians(lat2)

    mid = (

        sin(delta_lat / 2) ** 2
        + cos(lat1) * cos(lat2) 
        * sin(delta_lon / 2) ** 2

    )

    angular_distance = 2 * atan2(sqrt(mid), sqrt(1 - mid))

    return R * angular_distance

def get_shop_distances(shops, user_lat, user_lon):
        for shop in shops:
            shop.distance = round(
                haversine(
                    user_lat,
                    user_lon,
                    shop.latitude,
                    shop.longitude
                ), 
            2)
        shops.sort(key=lambda shop: shop.distance)
        return shops

def get_coordinates(postcode):
    try:
        response = urlopen(
            "https://api.postcodes.io/postcodes/" + postcode.strip()
        )

        data = json.load(response)
        result = data.get("result")

        if result is None:
            raise ValueError(
                f"Coordinates for postcode '{postcode}' not found."
            )

        return (
            result["latitude"],
            result["longitude"]
        )
 
    except (HTTPError, URLError, ValueError) as error:
         raise ValueError(
              f"Coordinates for postcode '{postcode}' not found."
         ) from error