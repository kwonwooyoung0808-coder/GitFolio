from pydantic import BaseModel, HttpUrl


class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl
    github_identity: str | None = None
    period: str | None = None
    scale: str | None = None
    role: str | None = None
