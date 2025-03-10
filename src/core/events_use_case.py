from src.db.dao.dao import EventDao
from src.db.database import connection
from src.db.schemas import EventPydantic


class EventUseCase:
    @classmethod
    @connection
    async def create_event(cls, session, event_data):
        event_model = EventPydantic(**event_data)

        result = await EventDao.create(session, event_model)

        return EventPydantic.model_validate(result).model_dump()

    @classmethod
    @connection
    async def get_events(cls, session):
        results = await EventDao.get_all(session)

        return [EventPydantic.model_validate(item).model_dump() for item in results]


event_use_case = EventUseCase()
