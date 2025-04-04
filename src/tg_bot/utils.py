import httpx

from  bot import logger
from  db.exceptions import PlaceNotFoundException
from  services.geolocation import get_map_image
from  tg_bot.keyboards.place_kbs import generate_places_kb
from  core.places_use_case import place_use_case


async def send_places_on_map(message, lat, lon, state):
    places = await place_use_case.get_places_by_point(center_lat=lat, center_lon=lon)
    await state.update_data(places=places)

    if len(places) == 0:
        await message.answer('К сожалению я ничего не нашел(')
        await state.clear()
        return

    try:
        map_image = await get_map_image(places, lat, lon)

        await message.answer_photo(
            photo=str(map_image),
            caption=f"Вот список ближайших мест:",
            reply_markup=generate_places_kb(places)
        )
    except httpx.HTTPStatusError as e:
        logger.error(f'API error: {e}')
        await message.answer(text=f"Вот список ближайших мест:", reply_markup=generate_places_kb(places))


async def callback_str_place_info(place_id):
    try:
        place_info = await place_use_case.get_place_info(place_id=place_id)

        return f"""
    📍<b>{place_info['title']}</b>
    {place_info['address']}
    
    ⭐️ Рейтинг: {place_info['rating']} / 5
    {f'💰 Средний чек: {place_info["avg_bill"]} ₽' if place_info['avg_bill'] != "" else ""}
    {f'✏️ Заметка: {place_info["note"]}' if place_info['note'] != "" else ""}
    
    🌍 <a href="https://2gis.ru/geo/{place_info['gis_id']}">Открыть на карте →</a>
    """

    except PlaceNotFoundException as e:
        logger.error(f'PlaceNotFound error: {e}')
        return "Не могу отобразить информацию("
