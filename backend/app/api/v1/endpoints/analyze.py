from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.analyze import AnalyzeRequest
from app.services.github.client import GitHubClient
from app.services.github.filter import filter_my_commits
from app.services.llm.claude_client import ClaudeClient
from app.services.llm.prompt_builder import build_prompt
from app.utils.sse import sse_event
from app.core.security import get_current_user

router = APIRouter()

@router.post("/stream")
async def analyze_stream(
    req: AnalyzeRequest,
    current_user: dict = Depends(get_current_user)
):
    """GitHub 레포 분석 - SSE 스트리밍 응답"""

    async def event_generator():
        try:
            yield sse_event("status", "레포 기본 정보 수집 중...")
            gh = GitHubClient(current_user["github_access_token"])
            repo_info = await gh.get_repo_info(req.repo_url)

            yield sse_event("status", "커밋 목록 수집 중...")
            all_commits = await gh.get_commits(req.repo_url)

            yield sse_event("status", f"커밋 필터링 중... (전체 {len(all_commits)}개)")
            my_commits = filter_my_commits(all_commits, req.github_id)
            yield sse_event("status", f"본인 기여 커밋 {len(my_commits)}개 추출 완료")

            yield sse_event("status", "변경 파일 분석 중...")
            diffs = await gh.get_diffs(req.repo_url, my_commits)

            yield sse_event("status", "AI 보고서 작성 시작...")
            prompt = build_prompt(repo_info, my_commits, diffs)

            claude = ClaudeClient()
            async for chunk in claude.stream(prompt):
                yield sse_event("chunk", chunk)

            yield sse_event("done", "분석 완료")

        except Exception as e:
            yield sse_event("error", str(e))

    return StreamingResponse(event_generator(), media_type="text/event-stream")
