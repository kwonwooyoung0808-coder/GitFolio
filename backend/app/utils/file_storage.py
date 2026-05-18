from pathlib import Path
from uuid import uuid4

from app.core.config import settings


def ensure_reports_dir() -> Path:
    reports_dir = Path(settings.REPORTS_DIR)
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def build_report_paths(prefix: str | None = None) -> dict:
    reports_dir = ensure_reports_dir()
    report_id = prefix or uuid4().hex
    return {
        "base_id": report_id,
        "pdf": reports_dir / f"{report_id}.pdf",
        "docx": reports_dir / f"{report_id}.docx",
    }
