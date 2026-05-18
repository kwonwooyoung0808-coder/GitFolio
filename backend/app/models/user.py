from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id               = Column(Integer, primary_key=True)
    github_id        = Column(String, unique=True, nullable=False)
    github_username  = Column(String, nullable=False)
    created_at       = Column(DateTime, server_default=func.now())
