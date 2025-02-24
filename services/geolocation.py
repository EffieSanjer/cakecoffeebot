import requests

from backend.config import settings
from services.gis import get_2gis_location


def get_place_index(page, total, i):
    return (page - 1) * total + i


def get_location(city: str = "Москва", location: str = None, lat: float = None, lon: float = None):
    if settings.GIS_API_KEY:
        return get_2gis_location(city, location, lat, lon)

    if not location:
        location = f"{lat},{lon}"

    response = requests.get(f"https://api.opencagedata.com/geocode/v1/json", {
        "key": settings.GEO_API_KEY,
        "language": "ru",
        "no_annotations": 1,
        "limit": 1,
        "countrycode": "ru",
        "q": f"{location},{city}"
    }, timeout=(5, 20))
    data = response.json()

    return {
        'name': data['results'][0]['formatted'],
        'geometry': data['results'][0]['geometry'],
    }


def get_map_image(places: list, lat: float = None, lon: float = None, page=1):
    markers_str = "|".join([f"lonlat:{p['lon']},{p['lat']};type:material;color:#4c905a;"
                            f"text:{get_place_index(page, len(places), i+1)}"
                            f";icontype:awesome" for (i, p) in enumerate(places)])

    response = requests.get(f"https://maps.geoapify.com/v1/staticmap", {
        "apiKey": settings.STATIC_MAP_API_KEY,
        "style": "maptiler-3d",
        "width": 600,
        "height": 600,
        "zoom": 13.5,
        "center": f"lonlat:{lon},{lat}",
        "marker": f"lonlat:{lon},{lat};type:awesome;color:#ca0000;size:large;icon:map-pin;iconsize:large;whitecircle:no|{markers_str}",
    }, timeout=(5, 20))

    if response.ok:
        return response.request.url

    return None


