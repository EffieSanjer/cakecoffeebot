import logging
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, create_engine, func, DateTime, asc
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import DeclarativeBase, relationship, Session

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

sqlite_database = "sqlite:///coffee_bot.db"
engine = create_engine(sqlite_database)


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    places = relationship("Place", back_populates="category")

    def __str__(self):
        return self.name


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    address = Column(String)
    city = Column(String)
    avg_bill = Column(String)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="places")

    note = Column(String)

    lon = Column(Numeric, index=True)
    lat = Column(Numeric, index=True)

    def __str__(self):
        return self.title

    @hybrid_method
    def lat_diff(self, center_lat):
        return round(center_lat, 6) - self.lat

    @hybrid_method
    def lon_diff(self, center_lon):
        return round(center_lon, 6) - self.lon

    @hybrid_method
    def is_point_in_circle(self, center_lat, center_lon, r) -> bool:
        return func.pow(self.lat_diff(center_lat), 2) + func.pow(self.lon_diff(center_lon), 2) <= func.pow(round(r, 6), 2)


def get_places_by_point(category_id, center_lat, center_lon, r):
    with (Session(autoflush=False, bind=engine) as db):
        places = db.query(Place).filter(Place.category_id == category_id).filter(
            Place.is_point_in_circle(center_lat, center_lon, r)
        ).all()
    return places


def get_place_by_id(place_id):
    with (Session(autoflush=False, bind=engine) as db):
        place = db.get(Place, place_id)
    return place


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    datetime = Column(DateTime, default=datetime.utcnow, index=True)
    address = Column(String)
    description = Column(String)
    tickets = Column(String)

    def __str__(self):
        return self.title


def create_event(info):
    with (Session(autoflush=False, bind=engine) as db):
        new_event = Event(**info)
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
    return new_event

def get_events():
    with (Session(autoflush=False, bind=engine) as db):
        today = datetime.today()
        events = db.query(Event).filter(
            Event.datetime.between(today, today + timedelta(31))
        ).order_by(Event.datetime).all()
    return events


# Base.metadata.create_all(bind=engine)
