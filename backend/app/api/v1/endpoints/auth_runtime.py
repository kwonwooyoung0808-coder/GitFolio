import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.security import create_jwt_token

router = APIRouter()


@router.get("/github")
def github_login():
    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        "&scope=repo,read:user"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
    )
    return RedirectResponse(url)


@router.get("/github/callback")
async def github_callback(code: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="GitHub OAuth exchange failed.")

        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        github_user = user_response.json()

    jwt_token = create_jwt_token(
        {
            "github_id": str(github_user["id"]),
            "github_username": github_user["login"],
            "github_access_token": access_token,
        }
    )
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}")
