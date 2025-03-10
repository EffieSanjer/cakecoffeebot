import json
import re

import requests

from src.config import settings
from src.services.gis import get_2gis_location, add_2gis_location
from src.core.places_use_case import place_use_case


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


async def add_new_location(link: str, cats: str, note: str = None):
    if settings.GIS_API_KEY:
        return await add_2gis_location(link, cats.title(), note)

    response = requests.get(link, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}, timeout=(5, 20))

    data = re.search(r'{"\d{6,}":{"data":(.*?),"meta"', response.text).group(1)
    formatted = json.loads(data)

    city = next((item["name"] for item in formatted['adm_div'] if item["type"] == "city"), None)
    avg_bill = None

    if 'attribute_groups' in formatted:
        for attr in formatted['attribute_groups']:
            avg_bill = next(
                (item["name"] for item in attr['attributes'] if item["tag"] == "food_service_avg_price"),
                None)
            if avg_bill is not None:
                avg_bill = re.search(r'\d{3,}', avg_bill)[0]
                break

    new_place = await place_use_case.create_place(
        place_data={
            'title': re.search(f"^([^,]+)", formatted['name']).group(1),
            'address': formatted['address_name'] if 'address_name' in formatted else 'None',
            'city': city,
            'avg_bill': avg_bill,
            'gis_id': formatted['id'],
            'lon': formatted['point']['lon'],
            'lat': formatted['point']['lat'],
            'note': note if note is not None else None
        },
        categories=cats.title().split(','))

    return new_place
