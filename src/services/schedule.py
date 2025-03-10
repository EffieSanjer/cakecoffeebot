from datetime import datetime

from src.core.events_use_case import event_use_case


def get_closest_events():
    events = event_use_case.get_events()
    return events


def add_event(info: list):
    event = event_use_case.create_event({
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
