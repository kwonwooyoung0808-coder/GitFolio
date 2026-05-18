import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.analysis_request import AnalysisRequest
from app.models.report import Report
from app.models.user import User

router = APIRouter()


def _get_user(db: Session, github_id: str) -> User:
    user = db.query(User).filter(User.github_id == str(github_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User record not found.")
    return user


def _get_owned_report(db: Session, report_id: int, github_id: str) -> tuple[Report, AnalysisRequest]:
    user = _get_user(db, github_id)
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    request_row = db.query(AnalysisRequest).filter(AnalysisRequest.id == report.request_id).first()
    if not request_row or request_row.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this report.")
    return report, request_row


@router.get("")
async def get_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _get_user(db, current_user["github_id"])
    requests = (
        db.query(AnalysisRequest)
        .filter(AnalysisRequest.user_id == user.id)
        .order_by(AnalysisRequest.created_at.desc())
        .all()
    )

    request_map = {item.id: item for item in requests}
    reports = (
        db.query(Report)
        .filter(Report.request_id.in_(request_map.keys() or [-1]))
        .order_by(Report.created_at.desc())
        .all()
    )

    payload = []
    for report in reports:
        content = json.loads(report.content_json)
        request_row = request_map[report.request_id]
        payload.append(
            {
                "id": report.id,
                "request_id": report.request_id,
                "project_name": content.get("project_name", "GitFolio Report"),
                "repo_name": content.get("repo", {}).get("full_name", request_row.repo_url),
                "created_at": report.created_at.isoformat(),
            }
        )
    return {"reports": payload}


@router.get("/{report_id}")
async def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    report, request_row = _get_owned_report(db, report_id, current_user["github_id"])
    content = json.loads(report.content_json)
    return {
        "id": report.id,
        "request_id": report.request_id,
        "project_name": content.get("project_name", "GitFolio Report"),
        "repo_name": content.get("repo", {}).get("full_name", request_row.repo_url),
        "created_at": report.created_at.isoformat(),
        "content": content,
        "pdf_available": settings.ENABLE_PDF and bool(report.pdf_path),
        "docx_available": bool(report.docx_path),
    }


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = "pdf",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    report, _ = _get_owned_report(db, report_id, current_user["github_id"])
    if format.lower() == "pdf" and not settings.ENABLE_PDF:
        raise HTTPException(status_code=404, detail="PDF download is disabled in this deployment.")

    selected = report.pdf_path if format.lower() == "pdf" else report.docx_path
    if not selected:
        raise HTTPException(status_code=404, detail="Requested file does not exist.")

    file_path = Path(selected)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Generated file is missing on the server.")

    media_type = "application/pdf" if format.lower() == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(path=file_path, media_type=media_type, filename=file_path.name)
