import re
from html import escape


SECTION_LABELS = {
    "project_name": ["project name", "프로젝트명"],
    "period": ["project period", "개발 기간"],
    "scale": ["team size", "팀 규모"],
    "role": ["role", "담당 역할", "주요 역할"],
    "implementation": ["implementation", "주요 구현 내용"],
    "tech_stack": ["tech stack", "사용 기술"],
    "outcome": ["outcome", "성과 및 배운 점"],
}

PLACEHOLDER_PERIOD = "실제 프로젝트 진행 기간을 직접 입력하세요."
PLACEHOLDER_SCALE = "팀 프로젝트인지 개인 프로젝트인지 실제 기준으로 입력하세요."
PLACEHOLDER_ROLE = "실제 맡은 역할을 직접 입력하세요."

GENERIC_ROLE_PATTERNS = (
    "implemented and improved",
    "frontend developer",
    "backend developer",
    "full stack developer",
    "프론트엔드 개발자",
    "백엔드 개발자",
)


def _normalize_section_title(raw_title: str) -> str | None:
    lowered = raw_title.strip().lower()
    for key, aliases in SECTION_LABELS.items():
        if lowered in [alias.lower() for alias in aliases]:
            return key
    return None


def _extract_sections(text: str) -> dict:
    sections = {}
    current_key = "summary"
    buffer = []

    for line in text.splitlines():
        cleaned = line.strip()
        matched = None
        trailing = ""

        bracket_match = re.match(r"^\[([^\]]+)\]$", cleaned)
        colon_match = re.match(r"^([A-Za-z가-힣\s]+)\s*:\s*(.*)$", cleaned)

        if bracket_match:
            matched = _normalize_section_title(bracket_match.group(1))
        elif colon_match:
            matched = _normalize_section_title(colon_match.group(1))
            trailing = colon_match.group(2).strip()

        if matched:
            if buffer:
                sections[current_key] = "\n".join(buffer).strip()
            current_key = matched
            buffer = [trailing] if trailing else []
            continue

        buffer.append(line)

    if buffer:
        sections[current_key] = "\n".join(buffer).strip()
    return sections


def format_report_content(raw_text: str, repo_info: dict, commit_summary: dict) -> dict:
    sections = _extract_sections(raw_text)
    project_name = sections.get("project_name") or repo_info.get("name") or repo_info.get("full_name", "GitFolio Project")
    implementation_lines = _clean_implementation_lines(sections.get("implementation", "").splitlines())
    if not implementation_lines and commit_summary.get("top_files"):
        implementation_lines = _build_implementation_from_files(commit_summary)

    tech_stack = sections.get("tech_stack") or repo_info.get("language") or "Not specified"
    tech_stack_items = _clean_tech_stack_items(re.split(r"[,/\n]", tech_stack))

    return {
        "mode": "paid",
        "project_name": project_name,
        "period": sections.get("period") or "Analysis-generated summary",
        "scale": sections.get("scale") or "Repository contributor activity based",
        "role": sections.get("role") or "Implemented and improved core product features",
        "implementation": implementation_lines,
        "tech_stack": tech_stack_items or ["GitHub", "FastAPI", "React"],
        "outcome": sections.get("outcome") or sections.get("summary") or raw_text.strip(),
        "raw_text": raw_text.strip(),
        "copy_prompt": "",
        "manual_steps": [],
        "repo": {
            "full_name": repo_info.get("full_name", ""),
            "description": repo_info.get("description", ""),
            "stars": repo_info.get("stargazers_count", 0),
        },
        "commit_summary": commit_summary,
    }


def format_local_llm_report(raw_text: str, repo_info: dict, commit_summary: dict, prompt: str, repo_profile: dict) -> dict:
    sanitized_text = _sanitize_unverified_fields(raw_text)
    sections = _extract_sections(sanitized_text)

    project_name = repo_info.get("name") or repo_info.get("full_name", "GitFolio Project")
    implementation = _clean_implementation_lines(sections.get("implementation", "").splitlines())
    if len(implementation) < 2:
        implementation = _build_implementation(commit_summary, repo_profile)

    tech_stack_items = _clean_tech_stack_items(
        re.split(r"[,/\n]", sections.get("tech_stack", "")) if sections.get("tech_stack") else []
    )
    if not tech_stack_items:
        tech_stack_items = _build_tech_stack(repo_info, repo_profile)

    outcome = sections.get("outcome", "").strip() or _build_outcome([], commit_summary, repo_profile)
    role = _normalize_role(sections.get("role", ""))
    summary = repo_profile.get("overview") or _build_overview(repo_info, repo_profile)

    report = {
        "mode": "local-llm",
        "project_name": project_name,
        "summary": summary,
        "period": PLACEHOLDER_PERIOD,
        "scale": PLACEHOLDER_SCALE,
        "role": role,
        "implementation": implementation,
        "tech_stack": tech_stack_items,
        "outcome": outcome,
        "copy_prompt": prompt,
        "manual_steps": [],
        "repo": {
            "full_name": repo_info.get("full_name", ""),
            "description": repo_info.get("description", ""),
            "stars": repo_info.get("stargazers_count", 0),
        },
        "commit_summary": commit_summary,
        "repo_profile": repo_profile,
    }
    report["raw_text"] = _rebuild_raw_text(report)
    return report


def _sanitize_unverified_fields(raw_text: str) -> str:
    text = raw_text
    text = re.sub(r"(\[개발 기간\]\s*\n)(.*?)(?=\n\[|\Z)", r"\1직접 입력 필요\n", text, flags=re.DOTALL)
    text = re.sub(r"(\[팀 규모\]\s*\n)(.*?)(?=\n\[|\Z)", r"\1직접 입력 필요\n", text, flags=re.DOTALL)
    text = re.sub(r"(개발 기간\s*:\s*).*$", r"\1직접 입력 필요", text, flags=re.MULTILINE)
    text = re.sub(r"(팀 규모\s*:\s*).*$", r"\1직접 입력 필요", text, flags=re.MULTILINE)
    text = re.sub(r"(주요 역할\s*:\s*)", "담당 역할: ", text)
    return text


def build_free_report(repo_info: dict, my_commits: list, commit_summary: dict, prompt: str, repo_profile: dict) -> dict:
    overview = repo_profile.get("overview") or _build_overview(repo_info, repo_profile)
    implementation = _build_implementation(commit_summary, repo_profile)
    role = PLACEHOLDER_ROLE
    tech_stack = _build_tech_stack(repo_info, repo_profile)
    outcome = _build_outcome(my_commits, commit_summary, repo_profile)

    report = {
        "mode": "free",
        "project_name": repo_info.get("name") or repo_info.get("full_name", "GitFolio Project"),
        "summary": overview,
        "period": PLACEHOLDER_PERIOD,
        "scale": PLACEHOLDER_SCALE,
        "role": role,
        "implementation": implementation,
        "tech_stack": tech_stack,
        "outcome": outcome,
        "copy_prompt": prompt,
        "manual_steps": [
            "아래 프롬프트를 복사합니다.",
            "직접 사용할 수 있는 무료 AI 채팅 서비스에 붙여넣습니다.",
            "생성된 한국어 포트폴리오 문장을 검토하고 개발 기간, 팀 규모, 담당 역할을 실제 값으로 수정합니다.",
            "저장된 DOCX 초안을 기반으로 최종 문서를 다듬습니다.",
        ],
        "repo": {
            "full_name": repo_info.get("full_name", ""),
            "description": repo_info.get("description", ""),
            "stars": repo_info.get("stargazers_count", 0),
        },
        "repo_profile": repo_profile,
        "commit_summary": commit_summary,
    }
    report["raw_text"] = _rebuild_raw_text(report)
    return report


def _clean_implementation_lines(lines: list) -> list:
    cleaned = []
    for line in lines:
        normalized = str(line).strip()
        normalized = normalized.lstrip("- ").strip()
        if not normalized:
            continue
        if re.search(r"\.(py|ts|tsx|js|jsx|pkl|h5)\s+\((added|modified|deleted)", normalized, flags=re.IGNORECASE):
            continue
        if normalized.startswith("[") and normalized.endswith("]"):
            continue
        cleaned.append(normalized)
    return cleaned


def _clean_tech_stack_items(items: list) -> list:
    cleaned = []
    for item in items:
        token = str(item).strip().lstrip("- ").strip()
        if not token:
            continue
        cleaned.append(token)

    deduped = []
    seen = set()
    for item in cleaned:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _build_implementation_from_files(commit_summary: dict) -> list:
    lines = []
    for item in commit_summary.get("top_files", []):
        filename = item["filename"]
        lowered = filename.lower()
        if lowered.endswith((".csv", ".svg", ".png", ".jpg", ".jpeg", ".pkl", ".h5")):
            continue
        lines.append(_describe_file_role(filename, item["status"]))
        if len(lines) >= 4:
            break

    return lines or ["핵심 파일을 기준으로 프로젝트의 주요 구현 내용을 다시 정리할 필요가 있습니다."]


def _normalize_role(role_text: str) -> str:
    cleaned = role_text.strip()
    if not cleaned:
        return PLACEHOLDER_ROLE

    lowered = cleaned.lower()
    if any(pattern in lowered for pattern in GENERIC_ROLE_PATTERNS):
        return PLACEHOLDER_ROLE
    if "직접 입력" in cleaned:
        return PLACEHOLDER_ROLE
    return cleaned


def _rebuild_raw_text(report: dict) -> str:
    lines = [
        f"[프로젝트명]\n{report.get('project_name', '')}",
        f"[개발 기간]\n{PLACEHOLDER_PERIOD}",
        f"[팀 규모]\n{PLACEHOLDER_SCALE}",
        f"[담당 역할]\n{report.get('role', PLACEHOLDER_ROLE)}",
        "[주요 구현 내용]",
    ]
    lines.extend(f"- {item}" for item in report.get("implementation", []))
    lines.append("[사용 기술]")
    lines.append(", ".join(report.get("tech_stack", [])))
    lines.append("[성과 및 배운 점]")
    lines.append(report.get("outcome", ""))
    return "\n".join(lines).strip()


def _build_implementation(commit_summary: dict, repo_profile: dict) -> list:
    lines = []

    for feature in repo_profile.get("feature_highlights", [])[:4]:
        if feature not in lines:
            lines.append(feature)

    for feature in repo_profile.get("features", [])[:4]:
        if feature not in lines:
            lines.append(feature)
        if len(lines) >= 5:
            break

    if len(lines) < 4:
        for item in commit_summary.get("top_files", []):
            filename = item["filename"]
            lowered = filename.lower()
            if lowered.endswith((".csv", ".svg", ".png", ".jpg", ".jpeg")):
                continue
            lines.append(_describe_file_role(filename, item["status"]))
            if len(lines) >= 5:
                break

    return lines or ["저장소 구조와 핵심 파일을 기준으로 프로젝트의 주요 구현 내용을 정리했습니다."]


def _build_overview(repo_info: dict, repo_profile: dict) -> str:
    summary_source = repo_profile.get("summary_source") or ""
    project_type = repo_profile.get("project_type") or "소프트웨어 프로젝트"
    feature_highlights = repo_profile.get("feature_highlights", [])

    if summary_source:
        return f"{summary_source} 저장소 구조와 핵심 파일을 함께 분석한 결과, {project_type}로 확인됩니다."
    if feature_highlights:
        return f"이 저장소는 {project_type}이며, 주요 구현 내용으로는 {feature_highlights[0]}"
    return f"이 저장소는 {project_type}로 분류되며, 핵심 디렉터리와 실행 파일을 기준으로 프로젝트 목적을 정리했습니다."


def _build_outcome(my_commits: list, commit_summary: dict, repo_profile: dict) -> str:
    parts = []

    if repo_profile.get("project_type"):
        parts.append(f"저장소 구조 분석 결과 {repo_profile['project_type']} 성격이 확인되었습니다.")
    if repo_profile.get("tech_stack"):
        parts.append("기술 스택으로는 " + ", ".join(repo_profile["tech_stack"][:8]) + " 등이 확인되었습니다.")
    if my_commits:
        parts.append(
            f"본인 커밋 {len(my_commits)}개와 변경 파일 {commit_summary.get('file_count', 0)}개를 기준으로 초안을 생성했습니다."
        )
    if repo_profile.get("key_paths"):
        parts.append("핵심 확인 파일: " + ", ".join(repo_profile["key_paths"][:5]))

    return " ".join(parts) or "저장소 구조와 주요 파일을 기준으로 프로젝트 결과를 정리했습니다."


def _build_tech_stack(repo_info: dict, repo_profile: dict) -> list:
    stack = list(repo_profile.get("tech_stack", []))
    if repo_info.get("language") and repo_info["language"] not in stack:
        stack.insert(0, repo_info["language"])

    return stack or ["Git", "GitHub"]


def _describe_file_role(filename: str, status: str) -> str:
    path = filename.lower()
    name = filename.split("/")[-1]

    if path.endswith("readme.md"):
        return "README 문서를 통해 프로젝트 목적, 실행 방법, 기술 스택 정리가 확인됩니다."
    if "train" in path or "model" in path:
        return f"{name} 파일에서 모델 학습 또는 예측 관련 로직 구성이 확인됩니다."
    if path.endswith(".ipynb"):
        return f"{name} 노트북에서 데이터 탐색 또는 실험 과정이 정리되어 있습니다."
    if path.endswith(("app.py", "main.py")):
        return f"{name} 파일에서 애플리케이션 실행 흐름이나 핵심 기능 구현이 확인됩니다."
    return f"{name} 파일에서 프로젝트의 주요 {status} 작업이 진행된 흔적이 확인됩니다."


def report_to_html(report: dict) -> str:
    implementation_items = "".join(f"<li>{escape(item)}</li>" for item in report.get("implementation", []))
    tech_stack = ", ".join(report.get("tech_stack", []))
    outcome_html = "<br>".join(escape(line) for line in report.get("outcome", "").splitlines() if line.strip())
    prompt_html = "<br>".join(escape(line) for line in report.get("copy_prompt", "").splitlines() if line.strip())
    summary = escape(report.get("summary", ""))

    return f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          body {{
            font-family: Arial, sans-serif;
            padding: 32px;
            color: #1f2937;
            line-height: 1.6;
          }}
          h1 {{ font-size: 28px; margin-bottom: 8px; }}
          h2 {{ font-size: 18px; margin-top: 24px; margin-bottom: 8px; color: #1d4ed8; }}
          .meta {{ color: #6b7280; font-size: 13px; }}
          ul {{ padding-left: 20px; }}
          .card {{
            border: 1px solid #dbeafe;
            background: #f8fbff;
            border-radius: 12px;
            padding: 20px;
          }}
          .prompt {{
            white-space: pre-wrap;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
            font-size: 12px;
          }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>{escape(report.get("project_name", "GitFolio Report"))}</h1>
          <div class="meta">{escape(report.get("repo", {}).get("full_name", ""))}</div>
          <p>{escape(report.get("repo", {}).get("description", ""))}</p>
          <p>{summary}</p>
        </div>
        <h2>개발 기간</h2>
        <p>{escape(report.get("period", ""))}</p>
        <h2>팀 규모</h2>
        <p>{escape(report.get("scale", ""))}</p>
        <h2>담당 역할</h2>
        <p>{escape(report.get("role", ""))}</p>
        <h2>주요 구현 내용</h2>
        <ul>{implementation_items}</ul>
        <h2>사용 기술</h2>
        <p>{escape(tech_stack)}</p>
        <h2>성과 및 배운 점</h2>
        <p>{outcome_html}</p>
        <h2>복사용 프롬프트</h2>
        <div class="prompt">{prompt_html}</div>
      </body>
    </html>
    """
