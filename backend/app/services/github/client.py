import json
from base64 import b64decode

import httpx

from app.core.exceptions import GitHubAPIError
from app.utils.rate_limit import ensure_not_rate_limited

GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }

    def _parse_repo(self, repo_url: str) -> tuple[str, str]:
        parts = repo_url.rstrip("/").split("/")
        return parts[-2], parts[-1]

    @staticmethod
    def _ensure_success(response: httpx.Response) -> None:
        ensure_not_rate_limited(response)
        if response.status_code >= 400:
            raise GitHubAPIError(response.text)

    async def get_repo_info(self, repo_url: str) -> dict:
        owner, repo = self._parse_repo(repo_url)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=self.headers)
            self._ensure_success(response)
            return response.json()

    async def get_commits(self, repo_url: str, per_page: int = 100, max_pages: int = 5) -> list:
        owner, repo = self._parse_repo(repo_url)
        commits = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for page in range(1, max_pages + 1):
                response = await client.get(
                    f"{GITHUB_API}/repos/{owner}/{repo}/commits",
                    headers=self.headers,
                    params={"per_page": per_page, "page": page},
                )
                self._ensure_success(response)
                data = response.json()
                if not data:
                    break
                commits.extend(data)
                if len(data) < per_page:
                    break

        return commits

    async def get_diffs(self, repo_url: str, commits: list, max_commits: int = 20) -> list:
        owner, repo = self._parse_repo(repo_url)
        diffs = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for commit in commits[:max_commits]:
                sha = commit["sha"]
                response = await client.get(
                    f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}",
                    headers=self.headers,
                )
                self._ensure_success(response)
                diffs.append(response.json())

        return diffs

    async def get_repo_tree(self, repo_url: str, branch: str | None = None) -> list:
        owner, repo = self._parse_repo(repo_url)
        async with httpx.AsyncClient(timeout=30.0) as client:
            if not branch:
                repo_info = await self.get_repo_info(repo_url)
                branch = repo_info.get("default_branch", "main")

            ref_response = await client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}",
                headers=self.headers,
                params={"recursive": "1"},
            )
            self._ensure_success(ref_response)
            return ref_response.json().get("tree", [])

    async def get_file_content(self, repo_url: str, path: str) -> str:
        owner, repo = self._parse_repo(repo_url)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
                    headers=self.headers,
                )
                self._ensure_success(response)
                data = response.json()
                if data.get("encoding") == "base64":
                    decoded = b64decode(data["content"]).decode("utf-8", errors="ignore")
                    return decoded[:8000]
                return str(data.get("content", ""))[:8000]
        except Exception:
            return ""

    @staticmethod
    def dumps_cache(repo_info: dict, commits: list, diffs: list) -> str:
        return json.dumps({"repo_info": repo_info, "commits": commits, "diffs": diffs}, ensure_ascii=False)

    @staticmethod
    def loads_cache(raw_data: str) -> dict:
        return json.loads(raw_data)
