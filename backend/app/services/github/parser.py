import json
import re
from pathlib import PurePosixPath


CODE_PRIORITY_EXTENSIONS = {".py", ".ipynb", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs"}
LOW_PRIORITY_EXTENSIONS = {".csv", ".json", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".lock"}
EXCLUDED_KEY_FILE_EXTENSIONS = {".pkl", ".csv", ".png", ".jpg", ".jpeg", ".bin", ".zip", ".gif", ".ico"}

FEATURE_KEYWORDS = {
    "policy": "정책 기준에 따라 특정 입력이나 콘텐츠를 판별하는 기능이 포함되어 있습니다.",
    "block": "위험하거나 허용되지 않는 입력을 차단하는 흐름이 포함되어 있습니다.",
    "filter": "입력 데이터나 결과를 필터링하는 로직이 포함되어 있습니다.",
    "moderation": "유해성 판별 또는 모더레이션 성격의 기능이 포함되어 있습니다.",
    "prediction": "예측 모델 또는 추론 기능이 포함되어 있습니다.",
    "classif": "분류 모델을 활용하는 기능이 포함되어 있습니다.",
    "recommend": "추천 또는 개인화 로직이 포함되어 있습니다.",
    "chat": "대화형 입력 또는 챗 인터페이스 기능이 포함되어 있습니다.",
    "attendance": "관중 수요나 출석 데이터와 관련된 분석 기능이 포함되어 있습니다.",
    "dashboard": "결과를 시각적으로 보여주는 대시보드 화면이 포함되어 있습니다.",
    "streamlit": "브라우저에서 결과를 확인할 수 있는 Streamlit UI가 포함되어 있습니다.",
    "fastapi": "API 서버 또는 백엔드 엔드포인트 구현이 포함되어 있습니다.",
    "flask": "웹 서버 또는 백엔드 라우팅 구현이 포함되어 있습니다.",
    "react": "컴포넌트 기반 프론트엔드 UI가 포함되어 있습니다.",
}

TECH_STACK_PATTERNS = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
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
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "docker": "Docker",
    "tailwind": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "selenium": "Selenium",
}

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
    lines = [_clean_markdown(line) for line in readme_text.splitlines()]
    meaningful = [line for line in lines if line and len(line) > 8]
    if not meaningful:
        return ""

    selected = []
    for line in meaningful[:6]:
        selected.append(line)
        joined = " ".join(selected)
        if len(joined) > 180:
            break
    return " ".join(selected)[:220]


def _extract_feature_highlights(readme_text: str, fallback_features: list) -> list:
    lines = [line.rstrip() for line in readme_text.splitlines()]
    highlights = []

    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        lowered = stripped.lstrip("#").strip().lower()
        if lowered in {"features", "feature", "main features", "주요 기능", "기능", "핵심 기능"}:
            for candidate in lines[index + 1 : index + 8]:
                cleaned = _clean_markdown(candidate)
                if not cleaned:
                    if highlights:
                        break
                    continue
                if cleaned.startswith(("-", "*")):
                    cleaned = cleaned.lstrip("-* ").strip()
                if len(cleaned) >= 8:
                    highlights.append(cleaned)
            break

    if not highlights:
        bullet_lines = []
        for raw_line in lines:
            stripped = raw_line.strip()
            if stripped.startswith(("- ", "* ")) and len(stripped) > 8:
                bullet_lines.append(_clean_markdown(stripped[2:]))
        highlights = bullet_lines[:4]

    if not highlights:
        highlights = fallback_features[:4]

    deduped = []
    for item in highlights:
        if item and item not in deduped:
            deduped.append(item)
    return deduped[:5]


def _extract_tech_stack(repo_info: dict, paths: list, file_contents: dict, readme_text: str) -> list:
    stack = []

    if repo_info.get("language"):
        stack.append(repo_info["language"])

    stack.extend(_extract_tech_stack_from_readme(readme_text))

    combined = "\n".join(file_contents.values()).lower()
    for pattern, label in TECH_STACK_PATTERNS.items():
        if pattern in combined:
            stack.append(label)

    lower_paths = [path.lower() for path in paths]
    if any(path.endswith(".ipynb") for path in lower_paths):
        stack.append("Jupyter Notebook")

    return _dedupe_preserve_order(stack)


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

        for candidate in lines[index + 1 : index + 12]:
            candidate_stripped = candidate.strip()
            if not candidate_stripped:
                if collected:
                    break
                continue
            if candidate_stripped.startswith("#"):
                break

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
        lower = token.lower()
        mapped = None
        for pattern, label in TECH_STACK_PATTERNS.items():
            if pattern in lower:
                mapped = label
                break
        normalized.append(mapped or token)

    return _dedupe_preserve_order(normalized)


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

    for keyword, sentence in FEATURE_KEYWORDS.items():
        if keyword in combined_text and sentence not in features:
            features.append(sentence)

    if any(path.lower().endswith(".ipynb") for path in paths):
        features.append("데이터 탐색이나 실험 과정을 정리한 노트북이 포함되어 있습니다.")
    if any("train" in path.lower() for path in paths):
        features.append("모델 학습이나 실험 자동화를 위한 스크립트가 포함되어 있습니다.")
    if any(path.lower().endswith(".csv") for path in paths):
        features.append("분석용 데이터셋이나 전처리 결과물이 저장소에 포함되어 있습니다.")
    if "streamlit" in _find_content_by_suffix(file_contents, "requirements.txt").lower():
        features.append("브라우저에서 예측 결과를 확인할 수 있는 Streamlit 화면 구성이 포함되어 있습니다.")

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
    cleaned = re.sub(r"`+", "", text)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"[*_>#-]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _dedupe_preserve_order(items: list) -> list:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped
