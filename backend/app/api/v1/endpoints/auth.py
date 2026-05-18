from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import httpx
from app.core.config import settings
from app.core.security import create_jwt_token

router = APIRouter()

@router.get("/github")
def github_login():
    """GitHub OAuth 인증 시작"""
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&scope=repo,read:user"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
    )
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(code: str):
    """GitHub OAuth 콜백 - JWT 발급"""
    async with httpx.AsyncClient() as client:
        # Access Token 교환
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="GitHub 인증 실패")

        # 사용자 정보 조회
        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        github_user = user_res.json()

    jwt = create_jwt_token({
        "github_id": str(github_user["id"]),
        "github_username": github_user["login"],
        "github_access_token": access_token,
    })
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?token={jwt}")
