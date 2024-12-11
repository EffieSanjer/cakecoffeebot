from datetime import datetime

from models import get_events, create_event


def get_closest_events():
    events = get_events()
    return events


def add_event(info: list):
    event = create_event({
        'title': info[0],
        'datetime': datetime.strptime(info[1], '%d.%m.%Y %H:%M'),
        'address': info[2],
        'description': info[3] if len(info) > 3 else None,
        'tickets': info[4] if len(info) > 4 else None
    })

    msg = (f"<b>{event.title}</b>\n"
           f"{event.datetime.strftime('%d.%m.%Y %H:%M')}\n"
           f"{event.address}\n"
           f"{event.description}\n"
           f"Ссылка на билеты: {event.tickets if event.tickets is not None else 'нет'}")
    return msg
