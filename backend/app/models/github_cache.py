from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class GithubCache(Base):
    __tablename__ = "github_data_cache"
    id            = Column(Integer, primary_key=True)
    repo_url      = Column(String, unique=True, nullable=False)
    raw_data_json = Column(Text)
    fetched_at    = Column(DateTime, server_default=func.now())
