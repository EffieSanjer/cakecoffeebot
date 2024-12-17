import math
import random
from datetime import datetime

import pytz

from models import get_places_by_point, get_place_by_id


def get_daytime():
    # for other timezones (можно просто взять из сообщения пользователя)
    # tz = tzwhere.tzwhere()
    # timeZoneStr = tz.tzNameAt(lat, lng)

    return datetime.now(pytz.timezone('Europe/Moscow'))


def get_radius(lat, minutes):
    speed = 75  # средняя скорость человека в м/мин
    distance = speed * minutes  # расстояние за количество минут

    one_degree_lat_km = 111.32
    one_degree_lon_km = one_degree_lat_km * math.cos(math.radians(lat))

    # определение км в координатах
    km_in_lat = 1 / one_degree_lat_km
    km_in_lon = 1 / one_degree_lon_km

    # определение м в координатах
    met_in_lat = distance / 1000 * km_in_lat
    met_in_lon = distance / 1000 * km_in_lon

    # среднее значение для радиуса
    r = (met_in_lat + met_in_lon) / 2
    return r


def get_places(center_lat, center_lon, minutes=13, page=1):
    category_id = 2  # dinners
    now = get_daytime()
    if now.hour < 15:
        category_id = 1  # breakfasts

    paginator = get_places_by_point(category_id, center_lat, center_lon, get_radius(center_lat, minutes), page)
    print(paginator)
    return paginator


def get_place_info(place_id):
    place = get_place_by_id(place_id)
    msg = (f"<b>{place.title}</b>\n"
           f"{place.address}\n"
           f"Средний чек: {place.avg_bill}\n"
           f"Заметка: {place.note}\n"
           f"2ГИС: https://2gis.ru/spb/geo/{place.gis_id}")
    return msg
