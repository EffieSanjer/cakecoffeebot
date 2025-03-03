from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryPydantic(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class PlaceCreatePydantic(BaseModel):
    title: str
    address: str
    city: str
    avg_bill: str | None = None

    note: str | None = None
    gis_id: str

    lon: float
    lat: float

    model_config = ConfigDict(from_attributes=True)


class PlacePydantic(BaseModel):
    id: int
    title: str
    address: str
    city: str
    avg_bill: str | None

    note: str | None
    gis_id: str

    lon: float
    lat: float

    rating: float

    model_config = ConfigDict(from_attributes=True)


class SimplifiedPlacePydantic(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class RatingCreatePydantic(BaseModel):
    user_id: int
    place_gis_id: str
    rating: float

    model_config = ConfigDict(from_attributes=True)


class RatingPydantic(BaseModel):
    place: SimplifiedPlacePydantic
    rating: float

    model_config = ConfigDict(from_attributes=True)


class EventPydantic(BaseModel):
    title: str
    start_at: datetime
    address: str
    description: str | None
    tickets: str | None

    model_config = ConfigDict(from_attributes=True)
