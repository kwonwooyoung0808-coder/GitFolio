from datetime import datetime

from pydantic import BaseModel


class ReportSummary(BaseModel):
    id: int
    request_id: int
    project_name: str
    repo_name: str
    created_at: datetime


class ReportDetail(ReportSummary):
    content: dict
    pdf_available: bool
    docx_available: bool
