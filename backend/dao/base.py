from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDao:
    model = None

    @classmethod
    async def create(cls, session: AsyncSession, values: BaseModel):
        info = values.model_dump(exclude_unset=True)
        new_instance = cls.model(**info)
        session.add(new_instance)

        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

        return new_instance

    @classmethod
    async def get_one_or_none(cls, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)

        query = select(cls.model).filter_by(**filter_dict)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession, filters: BaseModel = None):
        query = select(cls.model)

        if filters:
            filter_dict = filters.model_dump(exclude_unset=True)
            query.filter_by(**filter_dict)

        result = await session.execute(query)
        return result.scalars().all()

