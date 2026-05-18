from fastapi import HTTPException


class GitHubAPIError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=502, detail=f"GitHub API error: {detail}")


class LLMError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=502, detail=f"LLM error: {detail}")


class RateLimitError(HTTPException):
    def __init__(self, detail: str = "GitHub API rate limit exceeded. Please try again shortly."):
        super().__init__(status_code=429, detail=detail)
