from datetime import datetime
from typing import List

from sqlalchemy import Column, ForeignKey, func, Table, select
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship, Mapped, mapped_column, column_property, declared_attr

from .database import Base, uniq_str


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[uniq_str]

    places: Mapped[list["Place"]] = relationship(
        "Place",
        secondary='category_place_table',
        back_populates='categories',
    )

    def __str__(self):
        return self.name


class Rating(Base):
    __tablename__ = "places_rating"

    place_id: Mapped[int] = mapped_column(ForeignKey('places.id'), index=True)
    user_id: Mapped[int]

    # TODO: few ratings
    rating: Mapped[float] = mapped_column(default=0)

    place: Mapped["Place"] = relationship("Place", back_populates='ratings')


class Place(Base):
    __tablename__ = "places"

    title: Mapped[str]
    address: Mapped[str]
    city: Mapped[str]
    avg_bill: Mapped[str | None]

    note: Mapped[str | None]
    gis_id: Mapped[str] = mapped_column(index=True)

    lon: Mapped[float] = mapped_column(index=True)
    lat: Mapped[float] = mapped_column(index=True)

    ratings: Mapped[List["Rating"]] = relationship(
        "Rating",
        back_populates='place',
        cascade='all, delete-orphan'
    )
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        lazy="select",
        secondary='category_place_table',
        back_populates='places')

    def __str__(self):
        return self.title

    @declared_attr
    def rating(cls):
        return column_property(
            select(func.coalesce(func.avg(Rating.rating), 0))
            .where(Rating.place_id == cls.id)
            .correlate_except(Rating)
            .scalar_subquery()
        )


category_place_table = Table(
    "category_place_table",
    Base.metadata,
    Column("category_id", ForeignKey("categories.id"), primary_key=True),
    Column("place_id", ForeignKey("places.id"), primary_key=True),
)


class Event(Base):
    __tablename__ = "events"

    title: Mapped[str]
    start_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), index=True)
    address: Mapped[str]
    description: Mapped[str | None]
    tickets: Mapped[str | None]

    def __str__(self):
        return self.title

