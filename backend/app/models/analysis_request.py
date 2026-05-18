from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"
    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    repo_url    = Column(String, nullable=False)
    github_id   = Column(String, nullable=False)  # 분석 대상 GitHub ID
    status      = Column(String, default="pending")  # pending | done | error
    created_at  = Column(DateTime, server_default=func.now())
