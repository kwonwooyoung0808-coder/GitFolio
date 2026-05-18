from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from app.core.security import get_current_user

router = APIRouter()

@router.get("")
async def get_reports(current_user: dict = Depends(get_current_user)):
    """보고서 생성 이력 조회"""
    # TODO: DB에서 본인 보고서 목록 반환
    return {"reports": []}

@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = "pdf",
    current_user: dict = Depends(get_current_user)
):
    """PDF 또는 DOCX 다운로드"""
    # TODO: report_id로 파일 경로 조회 후 반환
    pass
