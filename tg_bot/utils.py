from services.geolocation import get_map_image
from tg_bot.keyboards.place_kbs import generate_places_kb
from use_cases.places_use_case import place_use_case


async def send_places_on_map(message, lat, lon, state):
    places = await place_use_case.get_places_by_point(center_lat=lat, center_lon=lon)
    await state.update_data(places=places)

    map_image = get_map_image(places, lat, lon)
    if map_image is not None:
        await message.answer_photo(
            photo=map_image,
            caption=f"Вот список ближайших мест:",
            reply_markup=generate_places_kb(places)
        )
    else:
        await message.answer(text=f"Вот список ближайших мест:", reply_markup=generate_places_kb(places))


async def callback_str_place_info(place_id):
    place_info = await place_use_case.get_place_info(place_id=place_id)
    return f"""
📍<b>{place_info['title']}</b>
{place_info['address']}

⭐️ Ваш рейтинг: {place_info['rating']} / 5
{f'💰 Средний чек: {place_info["avg_bill"]} ₽' if place_info['avg_bill'] != "" else ""}
{f'✏️ Заметка: {place_info["note"]}' if place_info['note'] != "" else ""}

🌍 <a href="https://2gis.ru/geo/{place_info['gis_id']}">Открыть на карте →</a>
"""
