import json
import re
from pathlib import PurePosixPath


CODE_PRIORITY_EXTENSIONS = {".py", ".ipynb", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs"}
LOW_PRIORITY_EXTENSIONS = {".csv", ".json", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".lock"}
EXCLUDED_KEY_FILE_EXTENSIONS = {".pkl", ".csv", ".png", ".jpg", ".jpeg", ".bin", ".zip", ".gif", ".ico"}

FEATURE_RULES = [
    (
        ["policy", "guard", "moderation", "filter", "block", "검증", "정책", "차단", "유해"],
        "정책 기준에 따라 입력이나 결과를 검증하고 제어하는 흐름이 포함되어 있습니다.",
    ),
    (
        ["predict", "prediction", "forecast", "classif", "recommend", "추천", "예측", "분류"],
        "데이터를 기반으로 예측, 분류 또는 추천 결과를 생성하는 기능이 포함되어 있습니다.",
    ),
    (
        ["chat", "chatbot", "conversation", "prompt", "대화", "챗봇"],
        "대화형 입력이나 챗봇 상호작용 기능이 포함되어 있습니다.",
    ),
    (
        ["dashboard", "admin", "monitor", "visual", "대시보드", "시각화", "모니터링"],
        "처리 결과를 시각적으로 확인하거나 관리할 수 있는 화면 구성이 포함되어 있습니다.",
    ),
    (
        ["route", "routing", "directions", "지도", "경로", "길찾기", "보행", "이동 지원", "교통약자"],
        "지도 기반 경로 탐색이나 이동 지원 기능이 포함되어 있습니다.",
    ),
    (
        ["map api", "geolocation", "kakao", "tmap", "leaflet", "postgis", "latitude", "longitude", "지도", "위치 정보"],
        "지도 시각화, 위치 정보 조회 또는 공간 데이터 처리 기능이 포함되어 있습니다.",
    ),
    (
        ["transit", "bus", "subway", "odsay", "대중교통", "버스", "지하철"],
        "대중교통 경로 조회나 이동 편의 정보 연계 기능이 포함되어 있습니다.",
    ),
    (
        ["elevator", "facility", "amenity", "accessible", "wheelchair", "편의시설", "엘리베이터", "교통약자"],
        "접근성, 편의시설 또는 교통약자 지원 정보를 제공하는 기능이 포함되어 있습니다.",
    ),
    (
        ["report", "incident", "alert", "realtime", "websocket", "socket", "supabase realtime", "신고", "실시간"],
        "실시간 상태 반영이나 사용자 신고 처리 흐름이 포함되어 있습니다.",
    ),
    (
        ["document", "parser", "ocr", "extract", "문서", "파싱", "추출"],
        "문서나 외부 데이터를 파싱·정리하는 처리 흐름이 포함되어 있습니다.",
    ),
    (
        ["fastapi", "flask", "django", "express", "router", "endpoint", "api"],
        "백엔드 API 또는 서버 엔드포인트 구현이 포함되어 있습니다.",
    ),
    (
        ["react", "vue", "next.js", "nextjs", "frontend", "ui", "screen", "화면", "인터페이스"],
        "사용자 입력과 결과 확인을 위한 프론트엔드 화면 구성이 포함되어 있습니다.",
    ),
]

TECH_STACK_PATTERNS = {
    "python": "Python",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node ": "Node.js",
    "express": "Express",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "sqlalchemy": "SQLAlchemy",
    "jwt": "JWT",
    "pyjwt": "JWT",
    "jsonwebtoken": "JWT",
    "yaml": "YAML",
    "pyyaml": "YAML",
    "pytest": "Pytest",
    "docker compose": "Docker Compose",
    "react": "React",
    "vite": "Vite",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "streamlit": "Streamlit",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "joblib": "joblib",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "opencv": "OpenCV",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "mysql": "MySQL",
    "mysql2": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "pg": "PostgreSQL",
    "postgis": "PostGIS",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "supabase": "Supabase",
    "axios": "Axios",
    "react router": "React Router DOM",
    "react-router-dom": "React Router DOM",
    "framer motion": "Framer Motion",
    "recharts": "Recharts",
    "swiper": "Swiper",
    "lucide react": "Lucide React",
    "react markdown": "React Markdown",
    "react-markdown": "React Markdown",
    "gemini api": "Gemini API",
    "@google/genai": "Gemini API",
    "@google/generative-ai": "Gemini API",
    "bcryptjs": "bcryptjs",
    "multer": "Multer",
    "cookie-parser": "cookie-parser",
    "cors": "CORS",
    "serverless-http": "serverless-http",
    "kakao maps": "Kakao Maps API",
    "kakao map": "Kakao Maps API",
    "tmap api": "Tmap API",
    "tmap": "Tmap API",
    "odsay": "ODsay API",
    "websocket": "WebSocket",
    "docker": "Docker",
    "tailwindcss": "Tailwind CSS",
    "tailwind": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "selenium": "Selenium",
}

SORTED_TECH_STACK_PATTERNS = sorted(
    TECH_STACK_PATTERNS.items(),
    key=lambda item: len(item[0]),
    reverse=True,
)

TECH_STACK_SECTION_NAMES = {
    "tech stack",
    "stack",
    "technology",
    "technologies",
    "skills",
    "기술 스택",
    "사용 기술",
    "기술",
    "개발 환경",
}

CORE_TECH_STACKS = {
    "Python",
    "Node.js",
    "Express",
    "Java",
    "JavaScript",
    "TypeScript",
    "React",
    "Vite",
    "Next.js",
    "Streamlit",
    "FastAPI",
    "Flask",
    "Django",
    "Pandas",
    "NumPy",
    "joblib",
    "scikit-learn",
    "TensorFlow",
    "PyTorch",
    "OpenCV",
    "Matplotlib",
    "Seaborn",
    "XGBoost",
    "LightGBM",
    "MySQL",
    "PostgreSQL",
    "PostGIS",
    "SQLite",
    "MongoDB",
    "Supabase",
    "Kakao Maps API",
    "Tmap API",
    "ODsay API",
    "Gemini API",
    "Docker",
    "Tailwind CSS",
    "Jupyter Notebook",
}

SECONDARY_TECH_STACKS = {
    "SQLAlchemy",
    "JWT",
    "YAML",
    "Pytest",
    "Docker Compose",
    "Axios",
    "React Router DOM",
    "Framer Motion",
    "Recharts",
    "Swiper",
    "Lucide React",
    "React Markdown",
    "bcryptjs",
    "Multer",
    "cookie-parser",
    "CORS",
    "serverless-http",
    "Selenium",
}

HIGH_VALUE_SECONDARY_TECH_STACKS = {
    "SQLAlchemy",
    "JWT",
    "YAML",
    "Pytest",
    "Docker Compose",
}

TECH_STACK_PRIORITY = [
    "Python",
    "FastAPI",
    "Flask",
    "Django",
    "Streamlit",
    "Pandas",
    "NumPy",
    "scikit-learn",
    "TensorFlow",
    "PyTorch",
    "XGBoost",
    "LightGBM",
    "OpenCV",
    "Matplotlib",
    "Seaborn",
    "React",
    "TypeScript",
    "JavaScript",
    "Vite",
    "Next.js",
    "Node.js",
    "Express",
    "Tailwind CSS",
    "MySQL",
    "PostgreSQL",
    "PostGIS",
    "SQLite",
    "MongoDB",
    "Supabase",
    "SQLAlchemy",
    "JWT",
    "Pytest",
    "Docker",
    "Docker Compose",
    "Gemini API",
    "Kakao Maps API",
    "Tmap API",
    "ODsay API",
]


def _pattern_in_text(pattern: str, text: str) -> bool:
    lowered_pattern = pattern.lower()
    lowered_text = text.lower()

    if re.search(r"[a-z0-9]", lowered_pattern):
        escaped = re.escape(lowered_pattern)
        return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", lowered_text) is not None
    return lowered_pattern in lowered_text


def _normalize_stack_token(token: str) -> str | None:
    lowered = token.lower().strip()
    if not lowered:
        return None

    for pattern, label in SORTED_TECH_STACK_PATTERNS:
        if _pattern_in_text(pattern, lowered):
            return label
    return None


def _extract_source_imports(content: str, lowered_path: str) -> list[str]:
    imports = []

    if lowered_path.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")):
        patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
        ]
        for pattern in patterns:
            imports.extend(re.findall(pattern, content))
    elif lowered_path.endswith(".py"):
        patterns = [
            r'^\s*import\s+([a-zA-Z0-9_\.]+)',
            r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+',
        ]
        for pattern in patterns:
            imports.extend(re.findall(pattern, content, flags=re.MULTILINE))

    normalized = []
    for item in imports:
        token = item.split(".")[0].strip()
        if token:
            normalized.append(token)
    return normalized


def _short_patch_snippet(patch: str, max_lines: int = 3) -> str:
    if not patch:
        return ""

    lines = []
    for raw_line in patch.splitlines():
        if raw_line.startswith(("+++", "---", "@@")):
            continue
        if raw_line.startswith("+") or raw_line.startswith("-"):
            lines.append(raw_line[:140])
        if len(lines) >= max_lines:
            break
    return "\n".join(lines)


def summarize_diffs(diffs: list) -> dict:
    changed_files = []
    additions = 0
    deletions = 0

    for diff in diffs:
        for file_data in diff.get("files", []):
            filename = file_data.get("filename", "")
            ext = PurePosixPath(filename).suffix.lower()
            priority = 2
            if ext in CODE_PRIORITY_EXTENSIONS:
                priority = 0
            elif "readme" in filename.lower():
                priority = 1
            elif ext in LOW_PRIORITY_EXTENSIONS:
                priority = 3

            additions += file_data.get("additions", 0)
            deletions += file_data.get("deletions", 0)
            changed_files.append(
                {
                    "filename": filename,
                    "status": file_data.get("status", "modified"),
                    "additions": file_data.get("additions", 0),
                    "deletions": file_data.get("deletions", 0),
                    "changes": file_data.get("changes", 0),
                    "snippet": _short_patch_snippet(file_data.get("patch", "")),
                    "priority": priority,
                }
            )

    changed_files.sort(key=lambda item: (item["priority"], -item["changes"], item["filename"]))
    return {
        "file_count": len(changed_files),
        "additions": additions,
        "deletions": deletions,
        "top_files": changed_files[:12],
    }


def select_key_files(changed_files: list) -> list:
    priority_names = ["app.py", "main.py", "server.py", "README.md", "requirements.txt"]

    prioritized = []
    regular = []

    for item in changed_files:
        filename = item.get("filename", "")
        path = PurePosixPath(filename)
        if path.suffix.lower() in EXCLUDED_KEY_FILE_EXTENSIONS:
            continue
        if path.name in priority_names:
            prioritized.append(filename)
        else:
            regular.append(filename)

    ordered = []
    for filename in priority_names:
        for candidate in prioritized:
            if PurePosixPath(candidate).name == filename and candidate not in ordered:
                ordered.append(candidate)

    for candidate in regular:
        if candidate not in ordered:
            ordered.append(candidate)

    return ordered[:5]


def extract_notebook_text(content: str) -> str:
    try:
        notebook = json.loads(content)
        texts = []
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") not in {"code", "markdown"}:
                continue
            source = cell.get("source", [])
            if isinstance(source, list):
                texts.append("".join(source))
            else:
                texts.append(str(source))
        return "\n".join(texts)
    except Exception:
        return content[:3000]


def infer_repo_profile(repo_info: dict, tree: list, file_contents: dict) -> dict:
    paths = [item["path"] for item in tree if item.get("type") == "blob"]
    lower_paths = [path.lower() for path in paths]

    package_json = _get_first_content(file_contents, "package.json").lower()
    requirements_txt = _get_first_content(file_contents, "requirements.txt").lower()
    app_py = _find_content_by_suffix(file_contents, "app.py").lower()
    main_py = _find_content_by_suffix(file_contents, "main.py").lower()
    readme_text = _find_readme_text(file_contents)
    combined_text = "\n".join(file_contents.values()).lower()

    frontend_signals = []
    backend_signals = []
    data_signals = []

    if any(path.startswith("frontend/") for path in lower_paths):
        frontend_signals.append("frontend directory")
    if any(path.startswith("src/") for path in lower_paths) and any(name.endswith(("package.json", "vite.config.js")) for name in lower_paths):
        frontend_signals.append("src plus web bundler config")
    if "react" in package_json:
        frontend_signals.append("React dependency")
    if "vite" in package_json:
        frontend_signals.append("Vite dependency")

    if any(path.startswith("backend/") for path in lower_paths):
        backend_signals.append("backend directory")
    if any(path.endswith("requirements.txt") for path in lower_paths):
        backend_signals.append("Python requirements")
    if any(path.endswith(("app.py", "main.py")) for path in lower_paths):
        backend_signals.append("Python entry file")
    if "fastapi" in requirements_txt or "fastapi" in main_py:
        backend_signals.append("FastAPI")
    if "flask" in requirements_txt or "flask" in app_py:
        backend_signals.append("Flask")

    if any(path.endswith(".ipynb") for path in lower_paths):
        data_signals.append("Jupyter Notebook")
    if any(path.endswith(".csv") for path in lower_paths):
        data_signals.append("CSV dataset")
    if any(token in path for path in lower_paths for token in ("model", "train", "predict")):
        data_signals.append("ML script")

    summary_source = repo_info.get("description") or _extract_summary_from_readme(readme_text)
    project_type = _infer_project_type(frontend_signals, backend_signals, data_signals, paths)
    structure = _summarize_structure(paths)
    features = _infer_features(paths, combined_text, file_contents)
    feature_highlights = _extract_feature_highlights(readme_text, features)
    file_evidence_highlights = _extract_file_evidence_highlights(paths, file_contents)
    if file_evidence_highlights:
        merged_highlights = []
        for item in file_evidence_highlights + feature_highlights:
            if item not in merged_highlights:
                merged_highlights.append(item)
        feature_highlights = merged_highlights[:5]
    path_highlights = _extract_path_highlights(paths)
    if path_highlights:
        for item in path_highlights:
            if item not in feature_highlights:
                feature_highlights.append(item)
        feature_highlights = feature_highlights[:5]
    tech_stack = _extract_tech_stack(repo_info, paths, file_contents, readme_text)
    key_paths = _pick_key_paths(paths)
    overview = _build_overview(summary_source, project_type, feature_highlights, features)

    return {
        "project_type": project_type,
        "summary_source": summary_source,
        "overview": overview,
        "structure": structure,
        "frontend_present": bool(frontend_signals),
        "frontend_signals": frontend_signals,
        "backend_present": bool(backend_signals),
        "backend_signals": backend_signals,
        "data_signals": data_signals,
        "features": features,
        "feature_highlights": feature_highlights,
        "tech_stack": tech_stack,
        "key_paths": key_paths,
    }


def _get_first_content(file_contents: dict, filename: str) -> str:
    return file_contents.get(filename, "")


def _find_content_by_suffix(file_contents: dict, filename: str) -> str:
    lowered = filename.lower()
    for path, content in file_contents.items():
        if path.lower().endswith(lowered):
            return content
    return ""


def _find_readme_text(file_contents: dict) -> str:
    for path, content in file_contents.items():
        if path.lower().endswith("readme.md"):
            return content
    return ""


def _extract_summary_from_readme(readme_text: str) -> str:
    lines = readme_text.splitlines()
    paragraph = []
    collecting = False

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            if collecting and paragraph:
                break
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("!"):
            continue

        cleaned = _clean_markdown(stripped.lstrip("> ").strip())
        if not cleaned or _is_noise_line(cleaned):
            continue
        if re.match(r"^\d+\.\s", cleaned):
            continue
        lowered_cleaned = cleaned.lower()
        if any(token in lowered_cleaned for token in ["readme", "package.json", "requirements.txt", "커밋", "commit", "프롬프트", "diff"]):
            continue

        collecting = True
        paragraph.append(cleaned)
        if len(" ".join(paragraph)) > 220:
            break

    return " ".join(paragraph)[:220]


def _extract_feature_highlights(readme_text: str, fallback_features: list) -> list:
    lines = [line.rstrip() for line in readme_text.splitlines()]
    highlights = []
    explicit_feature_section = False

    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        lowered = stripped.lstrip("#").strip().lower()
        if lowered in {"features", "feature", "main features", "주요 기능", "기능", "핵심 기능"}:
            explicit_feature_section = True
            for candidate in lines[index + 1 : index + 8]:
                cleaned = _clean_markdown(candidate)
                if not cleaned:
                    if highlights:
                        break
                    continue
                if cleaned.startswith(("-", "*")):
                    cleaned = cleaned.lstrip("-* ").strip()
                if len(cleaned) >= 8 and not _is_noise_line(cleaned):
                    highlights.append(cleaned)
            break

    if not highlights and fallback_features:
        highlights = fallback_features[:4]

    if not highlights and explicit_feature_section:
        table_rows = []
        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped.startswith("|"):
                continue
            cleaned = _normalize_markdown_table_row(stripped)
            if cleaned and not _is_noise_line(cleaned):
                table_rows.append(cleaned)
        highlights = table_rows[:4]

    if not highlights:
        bullet_lines = []
        for raw_line in lines:
            stripped = raw_line.strip()
            if stripped.startswith(("- ", "* ")) and len(stripped) > 8:
                cleaned = _clean_markdown(stripped[2:])
                if not _is_noise_line(cleaned):
                    bullet_lines.append(cleaned)
        highlights = bullet_lines[:4]

    if not highlights:
        table_rows = []
        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped.startswith("|"):
                continue
            cleaned = _normalize_markdown_table_row(stripped)
            if cleaned and not _is_noise_line(cleaned):
                table_rows.append(cleaned)
        highlights = table_rows[:4]

    if not highlights:
        highlights = fallback_features[:4]

    deduped = []
    for item in highlights:
        cleaned = re.sub(r"^\d+\.\s*", "", item).strip()
        if cleaned and cleaned not in deduped:
            deduped.append(cleaned)
    return deduped[:5]


def _extract_path_highlights(paths: list) -> list:
    highlights = []
    lowered_paths = [path.lower() for path in paths]

    path_rules = [
        (["ocr"], "문서 이미지에서 OCR 기반으로 데이터를 추출"),
        (["report"], "분석 결과를 리포트 형태로 정리하고 저장"),
        (["chatbot", "chat"], "챗봇 또는 대화형 상담 기능을 제공"),
        (["upload"], "파일 업로드와 분석 요청 흐름을 처리"),
        (["dashboard", "mypage"], "대시보드나 마이페이지에서 결과를 조회"),
        (["gemini", "openai", "anthropic", "llm", "ai"], "AI 모델을 연동해 분석 또는 응답 생성 기능을 제공"),
        (["context", "language"], "상태 관리 흐름을 포함"),
    ]

    for patterns, sentence in path_rules:
        if any(any(pattern in path for pattern in patterns) for path in lowered_paths):
            highlights.append(sentence)

    return _dedupe_preserve_order(highlights)[:5]


def _extract_file_evidence_highlights(paths: list, file_contents: dict) -> list:
    highlights = []
    lowered_paths = [path.lower() for path in paths]
    evidence_text = "\n".join(
        [path.lower() for path in paths] + [content.lower() for content in file_contents.values()]
    )

    model_labels = [
        ("gru", "GRU"),
        ("lstm", "LSTM"),
        ("rnn", "RNN"),
        ("transformer", "Transformer"),
        ("cnn", "CNN"),
    ]
    for token, label in model_labels:
        if any(token in path for path in lowered_paths):
            if any(keyword in evidence_text for keyword in ["predict", "prediction", "forecast", "예측", "수요", "분류"]):
                highlights.append(f"{label} 기반 예측 모델을 구성")
            else:
                highlights.append(f"{label} 기반 모델 학습 파이프라인을 구성")
            break

    if any("streamlit" in path for path in lowered_paths) or "streamlit" in evidence_text:
        if any(keyword in evidence_text for keyword in ["predict", "prediction", "forecast", "예측", "분류", "recommend", "추천"]):
            highlights.append("Streamlit 기반 예측 결과 확인 및 시각화 화면 제공")
        else:
            highlights.append("Streamlit 기반 사용자 화면 제공")

    if any(keyword in evidence_text for keyword in ["predict", "prediction", "forecast", "예측", "demand", "수요"]):
        highlights.append("데이터 기반 예측 기능 구현")
    elif any(keyword in evidence_text for keyword in ["classif", "분류"]):
        highlights.append("데이터 분류 기능 구현")
    elif any(keyword in evidence_text for keyword in ["recommend", "추천"]):
        highlights.append("추천 기능 구현")

    if any(keyword in evidence_text for keyword in ["matplotlib", "seaborn", "plot", "chart", "visual", "시각화", "graph"]):
        highlights.append("예측 결과 및 데이터 시각화 구성")

    return _dedupe_preserve_order(highlights)[:5]


def _extract_tech_stack(repo_info: dict, paths: list, file_contents: dict, readme_text: str) -> list:
    stack = []

    readme_stack = _extract_tech_stack_from_readme(readme_text)
    stack.extend(readme_stack)

    manifest_stack = _extract_tech_stack_from_manifests(file_contents)
    stack.extend(manifest_stack)

    lower_paths = [path.lower() for path in paths]
    if any(path.endswith(".ipynb") for path in lower_paths):
        stack.append("Jupyter Notebook")

    stack.extend(_extract_tech_stack_from_paths(lower_paths))

    stack = _finalize_tech_stack(stack)

    if not stack:
        repo_language = repo_info.get("language")
        if repo_language:
            normalized_language = TECH_STACK_PATTERNS.get(repo_language.lower(), repo_language)
            stack.append(normalized_language)

    return stack


def _extract_tech_stack_from_readme(readme_text: str) -> list:
    if not readme_text:
        return []

    lines = readme_text.splitlines()
    collected = []

    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        lowered = stripped.lstrip("#").strip().lower()
        if lowered not in TECH_STACK_SECTION_NAMES:
            continue

        for candidate in lines[index + 1 : index + 24]:
            candidate_stripped = candidate.strip()
            if not candidate_stripped:
                continue
            if candidate_stripped.startswith(("## ", "# ")):
                break
            if candidate_stripped.startswith("###"):
                continue

            cleaned = _clean_markdown(candidate_stripped)
            if ":" in cleaned:
                _, cleaned = cleaned.split(":", 1)
                cleaned = cleaned.strip()
            parts = re.split(r"[,|/]| {2,}", cleaned)
            for part in parts:
                token = part.strip(" -•\t")
                if not token or len(token) <= 1:
                    continue
                collected.append(token)
        if collected:
            break

    normalized = []
    for token in collected:
        mapped = _normalize_stack_token(token)
        normalized.append(mapped or token)

    return _dedupe_preserve_order(normalized)


def _finalize_tech_stack(stack: list[str]) -> list[str]:
    stack = _dedupe_preserve_order(stack)

    if "TypeScript" in stack and "JavaScript" in stack:
        stack = [item for item in stack if item != "JavaScript"]

    priority_index = {name: index for index, name in enumerate(TECH_STACK_PRIORITY)}
    stack = sorted(stack, key=lambda item: (priority_index.get(item, 10_000), stack.index(item)))

    core_stack = [item for item in stack if item in CORE_TECH_STACKS]
    secondary_stack = [item for item in stack if item in SECONDARY_TECH_STACKS]

    if len(core_stack) >= 8:
        return core_stack[:10]

    if len(core_stack) >= 6:
        prioritized_secondary = [item for item in secondary_stack if item in HIGH_VALUE_SECONDARY_TECH_STACKS]
        return (core_stack + prioritized_secondary)[:10]

    if len(core_stack) >= 4:
        prioritized_secondary = [item for item in secondary_stack if item in HIGH_VALUE_SECONDARY_TECH_STACKS]
        return (core_stack + prioritized_secondary[:2])[:10]

    return (core_stack + secondary_stack[:4])[:10]


def _extract_tech_stack_from_manifests(file_contents: dict) -> list:
    stack = []

    for path, content in file_contents.items():
        lowered_path = path.lower()
        lowered_content = content.lower()

        if lowered_path.endswith("package.json"):
            try:
                package_json = json.loads(content)
            except Exception:
                package_json = {}

            dependency_sections = [
                package_json.get("dependencies", {}),
                package_json.get("devDependencies", {}),
                package_json.get("peerDependencies", {}),
            ]
            for section in dependency_sections:
                if not isinstance(section, dict):
                    continue
                for dependency_name in section.keys():
                    mapped = _normalize_stack_token(dependency_name)
                    if mapped:
                        stack.append(mapped)

        if lowered_path.endswith("requirements.txt"):
            for line in content.splitlines():
                package_name = line.strip().lower()
                if not package_name or package_name.startswith("#"):
                    continue
                package_name = re.split(r"[<>=~!]", package_name)[0].strip()
                mapped = _normalize_stack_token(package_name)
                if mapped:
                    stack.append(mapped)

        if lowered_path.endswith((".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")):
            imports = _extract_source_imports(content, lowered_path)
            for imported in imports:
                mapped = _normalize_stack_token(imported)
                if mapped:
                    stack.append(mapped)

    return _dedupe_preserve_order(stack)


def _extract_tech_stack_from_paths(lower_paths: list[str]) -> list:
    stack = []

    path_rules = [
        (".py", "Python"),
        ("tsconfig.json", "TypeScript"),
        ("vite.config", "Vite"),
        ("tailwind.config", "Tailwind CSS"),
        ("docker-compose", "Docker Compose"),
        ("dockerfile", "Docker"),
        ("streamlit", "Streamlit"),
        ("requirements.txt", "Python"),
        (".tsx", "React"),
        (".jsx", "React"),
    ]

    for lowered_path in lower_paths:
        for token, label in path_rules:
            if token in lowered_path:
                stack.append(label)

    return _dedupe_preserve_order(stack)


def _summarize_structure(paths: list) -> list:
    top_levels = {}
    for path in paths:
        top = path.split("/")[0]
        top_levels[top] = top_levels.get(top, 0) + 1
    return [
        {"name": name, "file_count": count}
        for name, count in sorted(top_levels.items(), key=lambda item: (-item[1], item[0]))[:8]
    ]


def _infer_features(paths: list, combined_text: str, file_contents: dict) -> list:
    features = []
    readme_text = _find_readme_text(file_contents).lower()
    path_text = "\n".join(paths).lower()
    evidence_text = "\n".join([readme_text, path_text])

    for patterns, sentence in FEATURE_RULES:
        if any(_pattern_in_text(pattern, evidence_text) for pattern in patterns) and sentence not in features:
            features.append(sentence)

    if any(path.lower().endswith(".ipynb") for path in paths):
        features.append("데이터 탐색이나 실험 과정을 정리한 노트북이 포함되어 있습니다.")
    if any("train" in path.lower() for path in paths):
        features.append("모델 학습이나 실험 자동화를 위한 스크립트가 포함되어 있습니다.")
    if any(path.lower().endswith(".csv") for path in paths):
        features.append("분석용 데이터셋이나 전처리 결과물이 저장소에 포함되어 있습니다.")
    if "streamlit" in _find_content_by_suffix(file_contents, "requirements.txt").lower() or "streamlit" in evidence_text:
        features.append("브라우저에서 예측 결과를 확인할 수 있는 Streamlit 화면 구성이 포함되어 있습니다.")
    if "jwt" in evidence_text or "authorization" in evidence_text or "bearer" in evidence_text:
        features.append("JWT 또는 토큰 기반 인증 흐름이 구현되어 있습니다.")
    if "sqlalchemy" in evidence_text:
        features.append("SQLAlchemy 기반 데이터 모델과 데이터베이스 연동 구성이 포함되어 있습니다.")
    if "pytest" in combined_text or any("test" in path.lower() for path in paths):
        features.append("단위 테스트 또는 검증용 테스트 코드가 포함되어 있습니다.")
    if any("docker" in path.lower() for path in paths):
        features.append("Docker 기반 개발 또는 실행 환경 구성이 포함되어 있습니다.")
    if "health" in evidence_text:
        features.append("시스템 상태를 점검하기 위한 헬스체크 또는 상태 확인 기능이 포함되어 있습니다.")

    return _dedupe_preserve_order(features)[:8]


def _infer_project_type(frontend_signals: list, backend_signals: list, data_signals: list, paths: list) -> str:
    if frontend_signals and backend_signals:
        return "풀스택 웹 서비스 프로젝트"
    if data_signals and any(path.endswith(".py") for path in paths):
        return "데이터 분석과 모델링을 포함한 파이썬 프로젝트"
    if frontend_signals:
        return "사용자 화면 중심의 프론트엔드 프로젝트"
    if backend_signals:
        return "API 또는 서버 로직 중심의 백엔드 프로젝트"
    return "소프트웨어 구현 및 실험 결과를 담은 프로젝트"


def _pick_key_paths(paths: list) -> list:
    preferred = []
    for path in paths:
        lowered = path.lower()
        if lowered.endswith(("readme.md", "app.py", "main.py", "package.json", "requirements.txt")):
            preferred.append(path)
        elif lowered.endswith((".py", ".ipynb", ".jsx", ".tsx")) and len(preferred) < 12:
            preferred.append(path)
    return preferred[:12]


def _build_overview(summary_source: str, project_type: str, feature_highlights: list, features: list) -> str:
    if summary_source:
        return f"{summary_source} 저장소 구조와 핵심 파일을 함께 분석한 결과, {project_type}로 확인됩니다."
    if feature_highlights:
        return f"이 저장소는 {project_type}이며, 주요 구현 내용으로는 {feature_highlights[0]}"
    if features:
        return f"이 저장소는 {project_type}이며, 주요 구현 내용으로는 {features[0]}"
    return f"이 저장소는 {project_type}로 분류되며, 핵심 디렉터리와 실행 파일을 기준으로 프로젝트 목적을 정리했습니다."


def _clean_markdown(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("|"):
        normalized = _normalize_markdown_table_row(stripped)
        if normalized:
            return normalized
        return ""

    cleaned = re.sub(r"`+", "", text)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"[*_>#-]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _normalize_markdown_table_row(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("|"):
        return ""
    if re.fullmatch(r"\|?[\s:\-]+\|[\s:\-\|]*", stripped):
        return ""

    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    cells = [cell for cell in cells if cell]
    if len(cells) < 2:
        return ""
    if cells[0] in {"기능", "항목", "구분", "설명"}:
        return ""

    left = _clean_markdown(cells[0])
    right = _clean_markdown(cells[1])
    if not left or not right:
        return ""
    return f"{left}: {right}"


def _is_noise_line(text: str) -> bool:
    lowered = text.lower().strip()
    if not lowered:
        return True

    noisy_tokens = (
        "install",
        "installation",
        "usage",
        "getting started",
        "quick start",
        "requirements",
        "environment",
        "setup",
        "run",
        "npm install",
        "pip install",
        "docker compose",
        "uvicorn",
        "localhost",
        "port ",
        "python 3.",
        "node ",
        "실행",
        "설치",
        "환경",
        "사용법",
        "시작하기",
        "포트",
        "권장",
        "fail closed",
        "기밀 유출",
        "도입을 추진",
        "리스크",
    )
    if any(token in lowered for token in noisy_tokens):
        return True

    if re.match(r"^(readme|todo|note)\b", lowered):
        return True

    return False


def _dedupe_preserve_order(items: list) -> list:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped
