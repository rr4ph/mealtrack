from math import radians, sin, cos, sqrt, atan2

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
            shop["distance"] = round(
                haversine(
                    user_lat,
                    user_lon,
                    shop["coordinates"]["latitude"],
                    shop["coordinates"]["longitude"]
                ), 
            2)
        shops.sort(key=lambda shop: shop["distance"])
        return shops