from sqlalchemy import Column, Integer, Float, String, DateTime
from .db import Base
from datetime import datetime, timezone

class Delivery(Base):

    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)

    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)

    # NEW FIELDS 👇
    vehicle_id = Column(Integer)
    route_id = Column(Integer)

    stop_order = Column(Integer)
    eta_minutes = Column(Float)


class Vehicle(Base):

    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_number = Column(String)

    capacity = Column(Integer)


class Route(Base):

    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer)

    stop_sequence = Column(String)

    total_time = Column(Float)


class Order(Base):

    __tablename__ = "orders"

    id = Column(Integer,primary_key=True,index=True)

    address = Column(String,nullable=True)

    latitude = Column(Float,nullable=False)
    logitude = Column(Float,nullable=False)

    package_weight = Column(Float,default=1.0)

    priority = Column(String,default="normal")

    status = Column(String,default="pending")

    created_at = Column(DateTime,default=datetime.now(timezone.utc))