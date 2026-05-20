import re
from html import escape


SECTION_LABELS = {
    "project_name": ["project name", "프로젝트명"],
    "main_task": ["main task", "주요 업무"],
    "period": ["project period", "개발 기간", "업무 기간"],
    "scale": ["team size", "팀 규모", "개발 인원"],
    "role": ["role", "담당 역할", "주요 역할"],
    "tech_stack": ["tech stack", "사용 기술", "기술 스택"],
    "details": ["details", "상세 내용"],
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

NOISY_TEXT_PATTERNS = (
    "python 3.",
    "node ",
    "port ",
    "권장",
    "install",
    "pip install",
    "npm install",
    "docker compose up",
    "uvicorn",
    "ollama",
    "model download",
    "모델 다운로드",
    "실행 방법",
    "환경 변수",
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
    project_name = _normalize_project_name(sections.get("project_name", ""), repo_info)
    tech_stack_items = _clean_tech_stack_items(re.split(r"[,/\n]", sections.get("tech_stack", "")))

    report = {
        "mode": "paid",
        "project_name": project_name,
        "summary": repo_info.get("description", ""),
        "main_task": sections.get("main_task", "").strip(),
        "role": _normalize_role(sections.get("role", "")),
        "period": sections.get("period", "").strip() or PLACEHOLDER_PERIOD,
        "scale": sections.get("scale", "").strip() or PLACEHOLDER_SCALE,
        "tech_stack": tech_stack_items or ["GitHub", "FastAPI", "React"],
        "details": _clean_details_text(sections.get("details", "").strip()),
        "implementation": [],
        "outcome": _clean_details_text(sections.get("details", "").strip()),
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
    if not report["main_task"]:
        report["main_task"] = "저장소 구조와 핵심 구현 흐름을 바탕으로 주요 업무를 직접 보완하세요."
    if not report["details"]:
        report["details"] = "저장소에서 확인한 구현 사실을 바탕으로 상세 내용을 직접 보완하세요."
    report["raw_text"] = _build_resume_text(report)
    report["copy_prompt"] = ""
    report["outcome"] = report["details"]
    return report


def format_local_llm_report(raw_text: str, repo_info: dict, commit_summary: dict, prompt: str, repo_profile: dict) -> dict:
    sanitized_text = _sanitize_unverified_fields(raw_text)
    sections = _extract_sections(sanitized_text)

    project_name = _normalize_project_name("", repo_info)
    main_task = _build_main_task(repo_profile)
    role = _normalize_role(sections.get("role", ""))
    tech_stack_items = _build_tech_stack(repo_info, repo_profile)
    details = _build_details(commit_summary, repo_profile)
    summary = repo_profile.get("overview") or _build_overview(repo_info, repo_profile)

    report = {
        "mode": "local-llm",
        "project_name": project_name,
        "summary": summary,
        "main_task": main_task,
        "period": PLACEHOLDER_PERIOD,
        "scale": PLACEHOLDER_SCALE,
        "role": role,
        "implementation": [],
        "tech_stack": tech_stack_items,
        "details": details,
        "outcome": details,
        "copy_prompt": prompt,
        "manual_steps": [],
        "repo": {
            "full_name": repo_info.get("full_name", ""),
            "description": repo_info.get("description", ""),
            "stars": repo_info.get("stargazers_count", 0),
        },
        "commit_summary": commit_summary,
        "repo_profile": repo_profile,
        "generation_prompt": prompt,
    }
    report["raw_text"] = _build_resume_text(report)
    return report


def build_free_report(repo_info: dict, my_commits: list, commit_summary: dict, prompt: str, repo_profile: dict) -> dict:
    summary = repo_profile.get("overview") or _build_overview(repo_info, repo_profile)
    main_task = _build_main_task(repo_profile)
    tech_stack = _build_tech_stack(repo_info, repo_profile)
    details = _build_details(commit_summary, repo_profile)

    report = {
        "mode": "free",
        "project_name": _normalize_project_name("", repo_info),
        "summary": summary,
        "main_task": main_task,
        "period": PLACEHOLDER_PERIOD,
        "scale": PLACEHOLDER_SCALE,
        "role": PLACEHOLDER_ROLE,
        "implementation": [],
        "tech_stack": tech_stack,
        "details": details,
        "outcome": details,
        "copy_prompt": prompt,
        "manual_steps": [
            "이력서용 복사본을 기준으로 기간, 인원, 담당 역할을 실제 값으로 수정합니다.",
            "표현이 과하거나 부족한 부분은 프로젝트 맥락에 맞게 직접 다듬습니다.",
            "완성한 문장을 DOCX 다운로드본과 함께 제출용 문서에 반영합니다.",
        ],
        "repo": {
            "full_name": repo_info.get("full_name", ""),
            "description": repo_info.get("description", ""),
            "stars": repo_info.get("stargazers_count", 0),
        },
        "repo_profile": repo_profile,
        "commit_summary": commit_summary,
        "generation_prompt": prompt,
    }
    report["raw_text"] = _build_resume_text(report)
    return report


def _sanitize_unverified_fields(raw_text: str) -> str:
    text = raw_text
    text = re.sub(r"(\[개발 기간\]\s*\n)(.*?)(?=\n\[|\Z)", r"\1직접 입력 필요\n", text, flags=re.DOTALL)
    text = re.sub(r"(\[업무 기간\]\s*\n)(.*?)(?=\n\[|\Z)", r"\1직접 입력 필요\n", text, flags=re.DOTALL)
    text = re.sub(r"(\[팀 규모\]\s*\n)(.*?)(?=\n\[|\Z)", r"\1직접 입력 필요\n", text, flags=re.DOTALL)
    text = re.sub(r"(\[개발 인원\]\s*\n)(.*?)(?=\n\[|\Z)", r"\1직접 입력 필요\n", text, flags=re.DOTALL)
    text = re.sub(r"(개발 기간\s*:\s*).*$", r"\1직접 입력 필요", text, flags=re.MULTILINE)
    text = re.sub(r"(업무 기간\s*:\s*).*$", r"\1직접 입력 필요", text, flags=re.MULTILINE)
    text = re.sub(r"(팀 규모\s*:\s*).*$", r"\1직접 입력 필요", text, flags=re.MULTILINE)
    text = re.sub(r"(개발 인원\s*:\s*).*$", r"\1직접 입력 필요", text, flags=re.MULTILINE)
    return text


def _clean_main_task(text: str) -> str:
    text = str(text).strip()
    if not text:
        return ""
    lowered = text.lower()
    if any(pattern in lowered for pattern in NOISY_TEXT_PATTERNS):
        return ""
    return text


def _normalize_project_name(candidate: str, repo_info: dict) -> str:
    repo_name = (repo_info.get("name") or "").strip()
    if repo_name:
        return repo_name

    full_name = (repo_info.get("full_name") or "").strip()
    if "/" in full_name:
        return full_name.split("/")[-1].strip()

    cleaned = str(candidate).strip()
    cleaned = re.sub(r"\s*github repository\s*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*repository\s*$", "", cleaned, flags=re.IGNORECASE)
    return cleaned or "GitFolio Project"


def _clean_tech_stack_items(items: list) -> list:
    cleaned = []
    for item in items:
        token = str(item).strip().lstrip("- ").strip()
        if not token:
            continue
        cleaned.append(token)
    return _dedupe_preserve_order(cleaned)


def _clean_details_text(text: str) -> str:
    cleaned = str(text).strip()
    if not cleaned:
        return ""
    cleaned = re.sub(r"본인 커밋 \d+개와 변경 파일 \d+개를 기준으로 초안을 생성했습니다\.?", "", cleaned)
    cleaned = re.sub(r"핵심 확인 파일\s*:\s*.*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"README\.md.*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


def _has_any_signal(text: str, tokens: list[str]) -> bool:
    lowered = text.lower()
    for token in tokens:
        lowered_token = token.lower()
        if re.search(r"[a-z0-9]", lowered_token):
            escaped = re.escape(lowered_token)
            if re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", lowered):
                return True
        elif lowered_token in lowered:
            return True
    return False


def _is_generic_feature_sentence(text: str) -> bool:
    cleaned = str(text).strip()
    return cleaned.endswith("포함되어 있습니다.") or cleaned.endswith("구성이 포함되어 있습니다.")


def _normalize_feature_highlight(text: str) -> str:
    cleaned = str(text).strip().lstrip("- ").strip()
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = cleaned.replace("|", " ")
    cleaned = re.sub(r"\(?(?:code|type)\s*\d+\)?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = cleaned.rstrip(".: ")
    return cleaned


def _feature_to_task_phrase(text: str) -> str:
    cleaned = _normalize_feature_highlight(text)
    cleaned = re.sub(r"(기능이 포함되어 있습니다|흐름이 포함되어 있습니다|구성이 포함되어 있습니다)$", "", cleaned).strip()
    cleaned = re.sub(r"(기능 제공|기능 구현|화면 구성|처리 흐름)$", "", cleaned).strip()
    return re.sub(r"\s+", " ", cleaned).strip()


def _feature_to_task_title(text: str) -> str:
    cleaned = _feature_to_task_phrase(text)
    if ":" in cleaned:
        cleaned = cleaned.split(":", 1)[0].strip()
    return cleaned


def _get_concrete_feature_highlights(repo_profile: dict) -> list[str]:
    highlights = []
    for item in repo_profile.get("feature_highlights", []):
        normalized = _normalize_feature_highlight(item)
        if normalized and not _is_generic_feature_sentence(normalized) and normalized not in highlights:
            highlights.append(normalized)
    return highlights


def _join_with_korean_and(items: list[str]) -> str:
    cleaned = [item for item in items if item]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    return ", ".join(cleaned[:-1]) + " 및 " + cleaned[-1]


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


def _build_resume_text(report: dict) -> str:
    tech_stack = ", ".join(report.get("tech_stack", []))
    lines = [
        f"프로젝트명 : {report.get('project_name', '')}",
        "",
        f"주요 업무 : {report.get('main_task', '')}",
        f"담당 역할 : {report.get('role', PLACEHOLDER_ROLE)}",
        f"기술 스택 : {tech_stack}",
        f"업무 기간 : {report.get('period', PLACEHOLDER_PERIOD)}",
        f"개발 인원 : {report.get('scale', PLACEHOLDER_SCALE)}",
        f"상세 내용 : {report.get('details', '')}",
    ]
    return "\n".join(lines).strip()


def _summary_to_main_task(summary_source: str) -> str:
    text = str(summary_source).strip()
    if not text:
        return ""

    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"^\S+는\s+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(입니다|입니다\.)$", "", text)
    text = text.replace("바탕으로", "기반으로")

    if "기반으로" in text:
        base, objective = text.split("기반으로", 1)
        base = re.sub(r"(개발자가 자신의|사용자가 자신의|사용자가|개발자가)\s+", "", base).strip()
        base = re.sub(r"[을를]\s*$", "", base).strip()
        objective = re.sub(r"할 수 있도록 만든\s*", "", objective).strip()
        objective = re.sub(r"(서비스|플랫폼|웹 서비스|웹앱|애플리케이션)\s*$", "", objective).strip()
        objective = re.sub(r"\b빠르게\s*", "", objective).strip()
        if "문장" in objective and any(token in objective for token in ["정리", "생성", "초안"]):
            objective = "이력서 초안 자동 생성"
        if "저장소" in base and "분석" not in base:
            base = base + " 분석"
        if base and objective:
            return f"{base} 기반 {objective} 서비스 개발"

    text = re.sub(r"(서비스|플랫폼|웹 서비스|웹앱|애플리케이션)\s*$", "", text).strip()

    if not text:
        return ""
    if "개발" in text:
        return text
    return text + " 서비스 개발"


def _summary_to_detail_sentence(summary_source: str) -> str:
    text = str(summary_source).strip()
    if not text:
        return ""

    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"^\S+는\s+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(입니다|입니다\.)$", "", text).strip()
    text = text.replace("바탕으로", "기반으로")

    if "기반으로" in text:
        base, objective = text.split("기반으로", 1)
        base = re.sub(r"(개발자가 자신의|사용자가 자신의|사용자가|개발자가)\s+", "", base).strip()
        base = re.sub(r"[을를]\s*$", "", base).strip()
        objective = re.sub(r"할 수 있도록 만든\s*", "", objective).strip()
        objective = re.sub(r"(서비스|플랫폼|웹 서비스|웹앱|애플리케이션)\s*$", "", objective).strip()
        objective = re.sub(r"\b빠르게\s*", "", objective).strip()
        if "문장" in objective and any(token in objective for token in ["정리", "생성", "초안"]):
            objective = "이력서 초안 자동 생성"
        if "저장소" in base and "분석" not in base:
            base = base + " 분석"
        if base and objective:
            return f"{base} 기반 {objective} 서비스를 구현하였습니다."

    if not text:
        return ""
    return text + " 서비스를 구현하였습니다."


def _build_main_task(repo_profile: dict) -> str:
    project_type = repo_profile.get("project_type", "프로젝트")
    summary_source = repo_profile.get("summary_source", "")
    features = repo_profile.get("feature_highlights", []) or repo_profile.get("features", [])
    features_text = " ".join(features)
    tech_stack = " ".join(repo_profile.get("tech_stack", []))
    concrete_highlights = _get_concrete_feature_highlights(repo_profile)

    summary_task = _summary_to_main_task(summary_source)
    if summary_task:
        return summary_task

    if concrete_highlights:
        task_phrases = []
        for highlight in concrete_highlights[:3]:
            phrase = _feature_to_task_title(highlight)
            if phrase and phrase not in task_phrases:
                task_phrases.append(phrase)
        if task_phrases:
            return _join_with_korean_and(task_phrases[:2]) + " 기능 개발"

    has_api = "FastAPI" in tech_stack or "Flask" in tech_stack or _has_any_signal(features_text, ["API", "엔드포인트", "백엔드"])
    has_ui = _has_any_signal(features_text, ["대시보드", "대화형", "챗", "시각", "인터페이스", "화면", "프론트엔드"])
    has_policy = _has_any_signal(features_text, ["정책", "판별", "차단", "검증", "유해"])
    has_data = _has_any_signal(features_text, ["데이터", "모델", "학습", "예측", "분류"])
    has_docs = _has_any_signal(features_text, ["문서", "파싱", "추출"])
    has_route = _has_any_signal(features_text, ["경로", "길찾기", "route", "routing", "보행", "이동 지원"])
    has_map = _has_any_signal(features_text, ["지도", "위치 정보", "공간 데이터", "geolocation", "kakao", "tmap", "leaflet", "postgis"])
    has_transit = _has_any_signal(features_text, ["대중교통", "버스", "지하철", "교통", "transit", "odsay"])
    has_accessibility = _has_any_signal(features_text, ["엘리베이터", "편의시설", "접근성", "교통약자", "wheelchair", "accessible"])
    has_realtime = _has_any_signal(features_text, ["실시간", "realtime", "websocket", "socket", "동기화"])
    has_reporting = _has_any_signal(features_text, ["신고", "report", "incident", "alert"])

    parts = []
    if has_api:
        parts.append("백엔드 API")
    if has_route or has_map or has_transit or has_accessibility:
        mobility_parts = []
        if has_route:
            mobility_parts.append("경로 탐색")
        if has_transit:
            mobility_parts.append("대중교통 정보 연계")
        if has_accessibility:
            mobility_parts.append("접근성 정보 제공")
        elif has_map and not mobility_parts:
            mobility_parts.append("지도 기반 위치 정보 제공")
        if mobility_parts:
            parts.append(_join_with_korean_and(mobility_parts) + " 기능")
    elif has_policy:
        if "입력" in features_text and "응답" in features_text:
            parts.append("입력·응답 검증 기능")
        else:
            parts.append("정책 기반 검증 기능")
    elif has_data:
        if "예측" in features_text or "분류" in features_text:
            parts.append("데이터 분석 및 예측 기능")
        else:
            parts.append("데이터 처리 기능")
    if has_ui:
        if "챗" in features_text:
            parts.append("사용자 인터페이스 연동")
        else:
            parts.append("대시보드 연동")
    if has_reporting or has_realtime:
        parts.append("실시간 상태 반영 기능")
    if has_docs:
        parts.append("문서 처리 기능")

    if parts:
        return _join_with_korean_and(parts) + " 개발"
    return f"{project_type}의 핵심 기능을 구현하고 저장소 구조를 정리"


def _build_details(commit_summary: dict, repo_profile: dict) -> str:
    summary_source = repo_profile.get("summary_source", "")
    features = repo_profile.get("feature_highlights", []) + repo_profile.get("features", [])
    features_text = " ".join(features)
    tech_stack = repo_profile.get("tech_stack", [])
    sentences = []
    concrete_highlights = _get_concrete_feature_highlights(repo_profile)

    summary_sentence = _summary_to_detail_sentence(summary_source)
    if summary_sentence:
        sentences.append(summary_sentence)

    top_file_names = [item.get("filename", "").lower() for item in commit_summary.get("top_files", [])]
    has_api = "FastAPI" in tech_stack or any("router" in path or "api" in path for path in top_file_names)
    has_workflow = any("workflow" in path for path in top_file_names)
    has_engine = any("engine" in path for path in top_file_names)
    has_ui = any(token in features_text for token in ["대화형", "챗", "대시보드", "시각", "화면", "지도"]) or any(
        path.endswith((".tsx", ".jsx")) for path in top_file_names
    )
    has_policy = _has_any_signal(features_text, ["정책", "판별", "차단", "검증"])
    has_docs = _has_any_signal(features_text, ["문서", "파싱", "추출"])
    has_ml = _has_any_signal(features_text, ["모델", "학습", "예측", "분류"])
    has_route = _has_any_signal(features_text, ["경로", "길찾기", "route", "routing", "보행", "이동 지원"])
    has_map = _has_any_signal(features_text, ["지도", "위치 정보", "공간 데이터", "geolocation", "kakao", "tmap", "leaflet", "postgis"])
    has_transit = _has_any_signal(features_text, ["대중교통", "버스", "지하철", "교통", "transit", "odsay"])
    has_accessibility = _has_any_signal(features_text, ["엘리베이터", "편의시설", "접근성", "교통약자", "wheelchair", "accessible"])
    has_realtime = _has_any_signal(features_text, ["실시간", "realtime", "websocket", "socket", "동기화"])
    has_reporting = _has_any_signal(features_text, ["신고", "report", "incident", "alert"])

    if concrete_highlights:
        primary_parts = []
        for highlight in concrete_highlights[:2]:
            phrase = _feature_to_task_phrase(highlight)
            if phrase and phrase not in primary_parts:
                primary_parts.append(phrase)
        if primary_parts:
            sentences.append(_join_with_korean_and(primary_parts) + " 기능을 구현하였습니다.")

        secondary_parts = []
        for highlight in concrete_highlights[2:4]:
            phrase = _feature_to_task_phrase(highlight)
            if phrase and phrase not in secondary_parts:
                secondary_parts.append(phrase)
        if secondary_parts:
            sentences.append(_join_with_korean_and(secondary_parts) + " 기능을 추가로 구성하였습니다.")

    core_parts = []
    if not sentences and (has_route or has_map or has_transit or has_accessibility or has_reporting):
        if has_route:
            core_parts.append("지도 기반 경로 탐색")
        elif has_map:
            core_parts.append("위치 정보 조회")
        if has_transit:
            core_parts.append("대중교통 정보 연계")
        if has_accessibility:
            core_parts.append("편의시설·접근성 정보 제공")
        if has_reporting and has_realtime:
            core_parts.append("신고 정보의 실시간 반영")
        elif has_reporting:
            core_parts.append("사용자 신고 처리")
        elif has_realtime:
            core_parts.append("실시간 상태 반영")
        sentences.append(_join_with_korean_and(core_parts) + " 흐름을 구현하였습니다.")
    elif not sentences and has_policy:
        if "입력" in features_text and "응답" in features_text:
            core_parts.append("입력과 응답을 단계별로 검증하고 유해하거나 허용되지 않은 요청을 차단하는 흐름")
        else:
            core_parts.append("정책 기준에 따라 입력과 결과를 판별하거나 제어하는 흐름")
    elif not sentences and has_ml:
        if "예측" in features_text or "분류" in features_text:
            core_parts.append("데이터를 기반으로 예측 또는 분류 결과를 생성하는 흐름")
        else:
            core_parts.append("데이터를 수집·처리하고 분석 결과를 도출하는 흐름")
    if has_docs:
        core_parts.append("문서 또는 입력 데이터를 파싱·가공하는 처리 흐름")
    if core_parts:
        sentences.append(_join_with_korean_and(core_parts) + "을 구현하였습니다.")

    architecture_parts = []
    if has_engine:
        architecture_parts.append("핵심 처리 엔진")
    if has_workflow:
        architecture_parts.append("기능별 워크플로우")
    if has_api:
        architecture_parts.append("API 엔드포인트")
    if architecture_parts:
        sentences.append(_join_with_korean_and(architecture_parts) + "를 분리 구성해 기능별 책임을 나누고 유지보수성을 고려한 구조를 마련하였습니다.")

    if has_ui and not concrete_highlights:
        if any(token in features_text for token in ["챗", "대화형"]):
            ui_subject = "챗봇 인터페이스"
        elif "지도" in features_text:
            ui_subject = "지도 기반 사용자 화면"
        elif "대시보드" in features_text:
            ui_subject = "대시보드 화면"
        else:
            ui_subject = "사용자 화면"
        sentences.append(f"{ui_subject}을 구성해 사용자 입력과 처리 결과를 확인할 수 있는 상호작용 환경을 제공하였습니다.")

    support_parts = []
    if "JWT" in tech_stack or "JWT" in features_text or "토큰 기반 인증" in features_text:
        support_parts.append("인증 및 접근 제어")
    if "SQLAlchemy" in tech_stack:
        support_parts.append("데이터 모델과 데이터베이스 연동")
    if "Supabase" in tech_stack and "데이터 모델과 데이터베이스 연동" not in support_parts:
        support_parts.append("백엔드 데이터 저장소 연동")
    if "Pytest" in tech_stack or "테스트" in features_text or any("test" in path for path in top_file_names):
        support_parts.append("테스트 기반 검증 구조")
    if "Docker" in tech_stack or "Docker Compose" in tech_stack or any("docker" in path for path in top_file_names):
        support_parts.append("개발 환경 재현을 위한 Docker 구성")
    if "헬스체크" in features_text or "상태 확인" in features_text or has_realtime:
        support_parts.append("운영 상태 점검 또는 실시간 동기화 흐름")
    if support_parts:
        sentences.append(_join_with_korean_and(support_parts[:4]) + "까지 포함해 서비스 운영과 확장성을 고려하였습니다.")

    if not sentences:
        feature_sentences = []
        for feature in features:
            cleaned = _normalize_feature_sentence(feature)
            if cleaned:
                feature_sentences.append(cleaned)
        if feature_sentences:
            sentences.append(" ".join(feature_sentences[:4]))

    text = " ".join(sentences[:4])
    return _clean_details_text(text) or "저장소 구조와 핵심 구현 파일을 기준으로 상세 내용을 직접 보완하세요."


def _normalize_feature_sentence(feature: str) -> str:
    text = str(feature).strip().lstrip("- ").strip()
    if not text:
        return ""
    lowered = text.lower()
    if any(pattern in lowered for pattern in NOISY_TEXT_PATTERNS):
        return ""
    if re.search(r"\bpython\s*3\.\d+", lowered):
        return ""
    if re.search(r"\bpostgresql\s*\d+", lowered):
        return ""
    return text


def _build_overview(repo_info: dict, repo_profile: dict) -> str:
    summary_source = repo_profile.get("summary_source") or ""
    project_type = repo_profile.get("project_type") or "소프트웨어 프로젝트"
    if summary_source:
        return f"{summary_source} 저장소 구조와 핵심 파일을 함께 분석한 결과, {project_type}로 확인되었습니다."
    return f"저장소 구조와 핵심 구현 파일을 바탕으로 {project_type}의 맥락을 정리했습니다."


def _build_tech_stack(repo_info: dict, repo_profile: dict) -> list:
    stack = list(repo_profile.get("tech_stack", []))
    return _dedupe_preserve_order(stack) or ["Git", "GitHub"]


def _describe_file_role(filename: str, status: str) -> str:
    path = filename.lower()
    name = filename.split("/")[-1]

    if path.endswith("readme.md"):
        return ""
    if "policy_engine" in path:
        return "정책 엔진 로직을 구성해 규칙 기반 판별 흐름을 구현했습니다."
    if "input_guard_workflow" in path:
        return "입력 검증 워크플로우를 구성해 위험 질의를 사전에 점검하는 흐름을 구현했습니다."
    if "response_guard_workflow" in path:
        return "응답 검증 워크플로우를 구성해 출력 결과를 정책 기준으로 검사하는 흐름을 구현했습니다."
    if "doc_parser_workflow" in path:
        return "문서 파싱 워크플로우를 구성해 정책 문서를 처리하는 흐름을 구현했습니다."
    if "chatbotpage" in path:
        return "챗봇 화면을 구현해 사용자 질의와 검증 결과를 확인할 수 있는 UI를 구성했습니다."
    if "auth" in path or "jwt" in path:
        return "인증 또는 토큰 처리 흐름을 구현했습니다."
    if "test" in path:
        return "테스트 코드를 구성해 주요 기능 검증 흐름을 마련했습니다."
    if "docker" in path:
        return "Docker 기반 실행 또는 개발 환경 구성을 포함했습니다."
    if "router" in path or "routes" in path or "api" in path:
        return f"{name} 파일에서 API 엔드포인트와 요청 처리 흐름을 구성했습니다."
    if "workflow" in path:
        return f"{name} 파일에서 주요 처리 워크플로우를 구현했습니다."
    if "engine" in path:
        return f"{name} 파일에서 핵심 처리 엔진 로직을 구성했습니다."
    if "model" in path and path.endswith(".py"):
        return f"{name} 파일에서 데이터 모델 또는 도메인 구조를 정의했습니다."
    if path.endswith((".tsx", ".jsx")):
        return f"{name} 파일에서 사용자 화면과 상호작용 흐름을 구현했습니다."
    if path.endswith(("app.py", "main.py")):
        return f"{name} 파일에서 애플리케이션 실행 흐름과 핵심 기능 구성을 확인했습니다."
    return f"{name} 파일에서 프로젝트의 주요 {status} 작업을 진행했습니다."


def _dedupe_preserve_order(items: list) -> list:
    deduped = []
    seen = set()
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def report_to_html(report: dict) -> str:
    tech_stack = ", ".join(report.get("tech_stack", []))
    details_html = "<br>".join(escape(line) for line in report.get("details", "").splitlines() if line.strip())
    copy_html = "<br>".join(escape(line) for line in report.get("copy_prompt", "").splitlines() if line.strip())
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
          .card {{
            border: 1px solid #dbeafe;
            background: #f8fbff;
            border-radius: 12px;
            padding: 20px;
          }}
          .copy {{
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
        <h2>주요 업무</h2>
        <p>{escape(report.get("main_task", ""))}</p>
        <h2>담당 역할</h2>
        <p>{escape(report.get("role", ""))}</p>
        <h2>기술 스택</h2>
        <p>{escape(tech_stack)}</p>
        <h2>업무 기간</h2>
        <p>{escape(report.get("period", ""))}</p>
        <h2>개발 인원</h2>
        <p>{escape(report.get("scale", ""))}</p>
        <h2>상세 내용</h2>
        <p>{details_html}</p>
        <h2>이력서용 복사본</h2>
        <div class="copy">{copy_html}</div>
      </body>
    </html>
    """
