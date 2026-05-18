from app.core.exceptions import RateLimitError


def ensure_not_rate_limited(response) -> None:
    if response.status_code != 403:
        return

    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining == "0":
        reset_at = response.headers.get("X-RateLimit-Reset")
        detail = "GitHub API rate limit exceeded."
        if reset_at:
            detail += f" Reset timestamp: {reset_at}."
        raise RateLimitError(detail=detail)
