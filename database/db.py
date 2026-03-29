from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = "postgresql://ai_route_optimizer_project_user:xDehKIS2olRLpgWgPGRIV52EWNbIilhm@dpg-d74g2dlm5p6s73f6mq0g-a/ai_route_optimizer_project"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()