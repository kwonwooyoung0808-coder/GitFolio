import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.analysis_request import AnalysisRequest
from app.models.github_cache import GithubCache
from app.models.report import Report
from app.models.user import User
from app.schemas.analysis import AnalyzeRequest
from app.services.github.client import GitHubClient
from app.services.github.filter import filter_my_commits
from app.services.github.parser import (
    extract_notebook_text,
    infer_repo_profile,
    select_key_files,
    summarize_diffs,
)
from app.services.llm.claude_client import ClaudeClient
from app.services.llm.ollama_client import OllamaClient
from app.services.llm.prompt_builder import build_prompt
from app.services.report.docx_generator import generate_docx
from app.services.report.formatter import build_free_report, format_local_llm_report
from app.services.report.pdf_generator import generate_pdf
from app.utils.file_storage import build_report_paths
from app.utils.sse import sse_event

router = APIRouter()


@router.post("/stream")
async def analyze_stream(
    req: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    async def event_generator():
        request_row = None
        try:
            github_id = str(current_user["github_id"])
            github_username = current_user["github_username"]
            github_identity = req.github_identity or github_username or github_id

            user = db.query(User).filter(User.github_id == github_id).first()
            if not user:
                user = User(github_id=github_id, github_username=github_username)
                db.add(user)
                db.commit()
                db.refresh(user)

            request_row = AnalysisRequest(
                user_id=user.id,
                repo_url=str(req.repo_url),
                github_id=str(github_identity),
                status="pending",
            )
            db.add(request_row)
            db.commit()
            db.refresh(request_row)

            repo_url = str(req.repo_url)
            gh = GitHubClient(current_user["github_access_token"])

            yield sse_event("status", "Repository metadata is being collected.")
            repo_info = await gh.get_repo_info(repo_url)

            yield sse_event("status", "Commit history is being fetched.")
            all_commits = await gh.get_commits(repo_url)

            yield sse_event("status", f"Filtering your contributions from {len(all_commits)} commits.")
            my_commits = filter_my_commits(all_commits, github_identity)
            yield sse_event("status", f"Identified {len(my_commits)} commits linked to your GitHub identity.")

            yield sse_event("status", "Analyzing changed files and diffs.")
            diffs = await gh.get_diffs(repo_url, my_commits)
            diff_summary = summarize_diffs(diffs)
            all_changed_files = [file for diff in diffs for file in diff.get("files", [])]

            yield sse_event("status", "Inspecting repository structure and key files.")
            repo_tree = await gh.get_repo_tree(repo_url, repo_info.get("default_branch"))
            tree_paths = [item["path"] for item in repo_tree if item.get("type") == "blob"]
            key_file_candidates = [
                "README.md",
                "package.json",
                "requirements.txt",
                "app.py",
                "main.py",
                "Dockerfile",
                "docker-compose.yml",
                "docker-compose.yaml",
            ]
            for item in diff_summary.get("top_files", [])[:12]:
                filename = item.get("filename")
                if filename:
                    key_file_candidates.append(filename)

            for path in tree_paths:
                lowered = path.lower()
                if any(
                    token in lowered
                    for token in [
                        "/tests/",
                        "test_",
                        "__tests__",
                        "/docs/",
                        "generated_reports/",
                        "/screenshots/",
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".gif",
                    ]
                ):
                    continue
                if lowered.endswith(
                    (
                        "app.py",
                        "main.py",
                        "package.json",
                        "requirements.txt",
                        "readme.md",
                        ".ipynb",
                        "dockerfile",
                        "docker-compose.yml",
                        "docker-compose.yaml",
                    )
                ):
                    key_file_candidates.append(path)
                if any(
                    token in lowered
                    for token in [
                        "policy",
                        "filter",
                        "block",
                        "predict",
                        "train",
                        "dashboard",
                        "streamlit",
                        "auth",
                        "jwt",
                        "ocr",
                        "report",
                        "chat",
                        "upload",
                        "health",
                        "score",
                        "guest",
                        "limit",
                        "action",
                        "gemini",
                        "mypass",
                        "mypage",
                    ]
                ):
                    key_file_candidates.append(path)

            file_contents = {}
            for path in list(dict.fromkeys(key_file_candidates))[:25]:
                try:
                    file_contents[path] = await gh.get_file_content(repo_url, path)
                except Exception:
                    continue
            repo_profile = infer_repo_profile(repo_info, repo_tree, file_contents)

            yield sse_event("status", "Reviewing key files for project context.")
            key_files = select_key_files(all_changed_files)
            llm_file_contents = {}
            for file_path in key_files:
                content = await gh.get_file_content(repo_url, file_path)
                if file_path.lower().endswith(".ipynb"):
                    content = extract_notebook_text(content)
                if content:
                    llm_file_contents[file_path] = content
                yield sse_event("status", f"Loaded {file_path}.")

            cache = db.query(GithubCache).filter(GithubCache.repo_url == repo_url).first()
            cache_payload = json.dumps(
                {
                    "repo_info": repo_info,
                    "commits": my_commits,
                    "diffs": diffs,
                    "repo_tree": repo_tree,
                    "repo_profile": repo_profile,
                    "file_contents": llm_file_contents,
                },
                ensure_ascii=False,
            )
            if cache:
                cache.raw_data_json = cache_payload
            else:
                db.add(GithubCache(repo_url=repo_url, raw_data_json=cache_payload))
            db.commit()

            yield sse_event("status", "Building a portfolio draft prompt.")
            prompt = build_prompt(repo_info, my_commits, diff_summary, file_contents=llm_file_contents)
            report_content = None

            if settings.USE_CLOUD_LLM:
                yield sse_event("status", f"Running cloud LLM with Claude model {settings.CLAUDE_MODEL}.")
                try:
                    claude_client = ClaudeClient()
                    llm_text = await claude_client.generate(prompt)
                    report_content = format_local_llm_report(llm_text, repo_info, diff_summary, prompt, repo_profile)
                    report_content["mode"] = "cloud-llm"
                    yield sse_event("status", "Cloud LLM draft generation completed.")
                except Exception:
                    yield sse_event("status", "Claude API was unavailable, so GitFolio is moving to the next available mode.")

            if report_content is None and settings.OLLAMA_ENABLED:
                yield sse_event("status", f"Running local LLM with Ollama model {settings.OLLAMA_MODEL}.")
                try:
                    ollama_client = OllamaClient()
                    llm_text = await ollama_client.generate(prompt)
                    report_content = format_local_llm_report(llm_text, repo_info, diff_summary, prompt, repo_profile)
                    yield sse_event("status", "Local LLM draft generation completed.")
                except Exception:
                    yield sse_event("status", "Local LLM was unavailable, so GitFolio is falling back to rule-based draft generation.")

            if report_content is None:
                yield sse_event("status", "Building a rule-based starter draft.")
                report_content = build_free_report(repo_info, my_commits, diff_summary, prompt, repo_profile)

            preview_chunks = [
                "GitFolio prepared your portfolio draft.\n\n",
                report_content["raw_text"],
            ]
            for chunk in preview_chunks:
                yield sse_event("chunk", chunk)

            paths = build_report_paths()
            pdf_path = ""
            if settings.ENABLE_PDF:
                try:
                    pdf_path = generate_pdf(report_content, paths["pdf"])
                except Exception:
                    yield sse_event("status", "PDF generation was skipped on this machine. DOCX is still available.")
            else:
                yield sse_event("status", "PDF download is disabled in this deployment. DOCX is still available.")

            docx_path = generate_docx(report_content, paths["docx"])

            report = Report(
                request_id=request_row.id,
                content_json=json.dumps(report_content, ensure_ascii=False),
                pdf_path=pdf_path,
                docx_path=docx_path,
            )
            db.add(report)
            request_row.status = "done"
            db.commit()
            db.refresh(report)

            yield sse_event(
                "done",
                {
                    "report_id": report.id,
                    "source": report_content["mode"],
                    "project_name": report_content["project_name"],
                },
            )
        except Exception as exc:
            if request_row:
                request_row.status = "error"
                db.commit()
            yield sse_event("error", str(exc))

    return StreamingResponse(event_generator(), media_type="text/event-stream")
