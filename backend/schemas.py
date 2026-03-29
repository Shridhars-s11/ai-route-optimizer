from pydantic import BaseModel
from typing import List


class Location(BaseModel):
    latitude: float
    longitude: float


class RouteRequest(BaseModel):
    locations: List[Location]
    vehicles: int
