from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Report(Base):
    __tablename__ = "reports"
    id           = Column(Integer, primary_key=True)
    request_id   = Column(Integer, ForeignKey("analysis_requests.id"))
    content_json = Column(Text)   # LLM 분석 결과 JSON
    pdf_path     = Column(String) # 생성된 PDF 파일 경로
    docx_path    = Column(String) # 생성된 DOCX 파일 경로
    created_at   = Column(DateTime, server_default=func.now())
