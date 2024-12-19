import re

import requests
from decouple import config

from models import Place, create_place


def get_2gis_location(city: str = "Москва", location: str = None, lat: float = None, lon: float = None):
    params = {
        "key": config('2GIS_API_KEY'),
        "locale": "ru_RU",
        "fields": "items.point"
    }

    if not location:
        location = f"{lat},{lon}"
    else:
        params['type'] = 'station.metro'

    params['q'] = f"{location},{city}"

    response = requests.get(f"https://catalog.api.2gis.com/3.0/items", params, timeout=(5, 20))
    data = response.json()

    points = data['result']['items'][0]['point']

    return {
        'name': data['result']['items'][0]['name'],
        'geometry': {'lat': points['lat'], 'lng': points['lon']},
    }


def add_2gis_location(link, cats, note):
    gis_id = re.search(r"\d{4,}", link)[0]

    response = requests.get(f"https://catalog.api.2gis.com/3.0/items/byid", {
        "key": config('2GIS_API_KEY'),
        "id": gis_id,
        "locale": "ru_RU",
        "fields": "items.point,items.context,items.adm_div"
    })
    data = response.json()
    print(data)

    formatted = data['result']['items'][0]
    city = next((item["name"] for item in formatted['adm_div'] if item["type"] == "city"), None)
    avg_bill = None

    if 'stop_factors' in formatted['context']:
        avg_bill = next((item["name"] for item in formatted['context']['stop_factors'] if item["tag"] == "food_service_avg_price"), None)
        if avg_bill is not None:
            avg_bill = re.search(r'\d{3,}', avg_bill)[0]

    new_place = create_place({
        'title': re.search(f"(.+),.+$", formatted['name']).group(1),
        'address': formatted['address_name'] if 'address_name' in formatted else 'None',
        'city': city,
        'avg_bill': avg_bill,
        'gis_id': formatted['id'],
        'lon': formatted['point']['lon'],
        'lat': formatted['point']['lat'],
        'note': note if note is not None else None
    }, cats.split(','))

    return new_place
