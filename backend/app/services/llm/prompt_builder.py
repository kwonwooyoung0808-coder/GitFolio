from pathlib import PurePosixPath


def _pattern_in_text(pattern: str, text: str) -> bool:
    lowered_pattern = pattern.lower()
    lowered_text = text.lower()

    if any(char.isalnum() for char in lowered_pattern):
        import re

        escaped = re.escape(lowered_pattern)
        return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", lowered_text) is not None
    return lowered_pattern in lowered_text


def build_prompt(repo_info: dict, my_commits: list, diff_summary: dict, file_contents: dict = {}) -> str:
    contribution_summary = _build_contribution_summary(my_commits, diff_summary)

    code_fact_section = ""
    if file_contents:
        code_fact_section = "\n\n=== 저장소 전체 코드 근거 기반 구현 사실 ===\n" + _render_code_facts(file_contents)

    return f"""
당신은 한국어 이력서와 포트폴리오 문장을 작성하는 전문가입니다.
아래 GitHub 저장소와 본인 기여 요약을 바탕으로 실제 이력서에 넣을 수 있는 프로젝트 소개 문장을 작성하세요.
반드시 제공된 저장소 정보와 핵심 구현 사실만 바탕으로 작성하세요.
코드에서 확인되지 않은 내용은 추측하지 마세요.

출력 형식은 반드시 아래 순서를 지켜 주세요.
프로젝트명 :
주요 업무 :
담당 역할 :
기술 스택 :
업무 기간 :
개발 인원 :
상세 내용 :

작성 규칙:
- 프로젝트명은 반드시 저장소 이름의 마지막 부분만 사용하세요.
  예: kwonwooyoung0808-coder/SafeAgent -> SafeAgent
- 프로젝트명에 GitHub Repository, Repo, Project 같은 보조 표현을 붙이지 마세요.
- 개발 기간과 개발 인원은 저장소만으로 확정할 수 없으므로 "직접 입력 필요"로 작성하세요.
- 담당 역할도 저장소만으로 확정되지 않으면 "직접 입력 필요"로 작성하세요.
- 주요 업무는 한 줄로, 서비스의 핵심 책임을 요약하세요.
- 상세 내용은 2~4문장 정도의 자연스러운 이력서 문체로 작성하세요.
- 설치 방법, 버전 정보, 포트 번호, 모델 다운로드 방법, 실행 명령은 쓰지 마세요.
- 커밋 수, 변경 파일 수, 핵심 확인 파일 목록 같은 메타 정보는 결과 문장에 쓰지 마세요.
- 파일명 나열보다 기능, 처리 흐름, 구현 목적을 중심으로 작성하세요.
- 기술 스택은 쉼표로 구분해 한 줄로 정리하세요.
- 주요 업무와 상세 내용은 저장소 전체 기능 흐름과 구현 구조를 우선 참고해 작성하세요.
- "본인 확인 기여 요약"은 담당 역할이나 강조 포인트를 잡기 위한 보조 참고 자료로만 사용하세요.
- 저장소 전체에서 확인되는 기능과 본인 기여 요약이 다를 때는, 프로젝트 전체 흐름을 왜곡하지 말고 자연스럽게 함께 반영하세요.
- 아래의 "본인 확인 기여 요약"은 이력서용 문장을 만들기 위한 참고 재료이지, 그대로 복붙할 문장이 아닙니다.

저장소 정보
- 이름: {repo_info.get('full_name', '')}
- 설명: {repo_info.get('description', '설명 없음')}
- 대표 언어: {repo_info.get('language', '미확인')}
- 스타 수: {repo_info.get('stargazers_count', 0)}

본인 확인 기여 요약
{contribution_summary}{code_fact_section}
"""


def _build_contribution_summary(my_commits: list, diff_summary: dict) -> str:
    bullets = []

    commit_messages = []
    for commit in my_commits[:6]:
        message = commit.get("commit", {}).get("message", "").splitlines()[0].strip()
        if message:
            commit_messages.append(message)
    if commit_messages:
        bullets.append("- 커밋 흐름 요약: " + "; ".join(commit_messages[:4]))

    file_roles = []
    for item in diff_summary.get("top_files", [])[:10]:
        role = _summarize_changed_file(item.get("filename", ""))
        if role and role not in file_roles:
            file_roles.append(role)
        if len(file_roles) >= 4:
            break
    if file_roles:
        bullets.append("- 변경 파일 기준 기여 범위: " + "; ".join(file_roles))

    file_count = diff_summary.get("file_count", 0)
    if file_count:
        bullets.append("- 본인 커밋 기준으로 여러 파일에 걸친 기능 추가 또는 구조 변경 이력이 확인됩니다.")

    return "\n".join(bullets) or "- 본인 기여를 요약할 명확한 커밋/변경 파일 정보가 부족합니다."


def _summarize_changed_file(filename: str) -> str:
    path = filename.lower()
    name = PurePosixPath(filename).name

    if "policy_engine" in path:
        return "정책 엔진 로직 구현"
    if "input_guard_workflow" in path:
        return "입력 검증 워크플로우 구현"
    if "response_guard_workflow" in path:
        return "응답 검증 워크플로우 구현"
    if "doc_parser_workflow" in path:
        return "문서 파싱 워크플로우 구현"
    if "chatbotpage" in path:
        return "챗봇 화면 및 사용자 상호작용 구현"
    if "router" in path or "routes" in path:
        return "API 라우터 구성"
    if "model" in path and path.endswith(".py"):
        return "데이터 모델 구조 정의"
    if path.endswith((".tsx", ".jsx")):
        return f"{name} 기반 프론트엔드 화면 구현"
    if path.endswith(("main.py", "app.py")):
        return "애플리케이션 실행 및 서버 구성"
    return ""


def _render_code_facts(file_contents: dict) -> str:
    rendered = []

    for filename, content in file_contents.items():
        facts = _summarize_file_facts(filename, content)
        if not facts:
            continue
        rendered.append(f"- {filename}: {facts}")

    return "\n".join(rendered) or "- 핵심 파일에서 구현 의도를 추론할 만한 명확한 사실을 찾지 못했습니다."


def _summarize_file_facts(filename: str, content: str) -> str:
    lowered_name = PurePosixPath(filename).name.lower()
    lowered_path = filename.lower()
    lowered = content.lower()
    snippets = []

    if lowered_name == "requirements.txt":
        packages = []
        for package in [
            "fastapi",
            "flask",
            "streamlit",
            "pandas",
            "numpy",
            "scikit-learn",
            "sklearn",
            "tensorflow",
            "torch",
            "xgboost",
            "lightgbm",
        ]:
            if package in lowered:
                packages.append("scikit-learn" if package == "sklearn" else package)
        if packages:
            snippets.append("사용 라이브러리로 " + ", ".join(dict.fromkeys(packages)) + " 등이 확인됩니다.")

    if lowered_name == "package.json":
        packages = []
        for package in ["react", "vite", "next", "axios", "zustand", "tailwindcss"]:
            if package in lowered:
                packages.append("Next.js" if package == "next" else package)
        if packages:
            snippets.append("프론트엔드 구성 요소로 " + ", ".join(dict.fromkeys(packages)) + " 등이 확인됩니다.")

    if any(token in lowered_path for token in ["config/", "/config", "env.js", ".env", "settings", "config.js"]):
        snippets.append("환경 변수 또는 서비스 설정 구성이 확인됩니다.")

    if lowered_name in {"app.py", "main.py", "server.py"}:
        if "fastapi" in lowered:
            snippets.append("FastAPI 엔드포인트 또는 서버 실행 구성이 확인됩니다.")
        if "flask" in lowered:
            snippets.append("Flask 기반 서버 실행 또는 라우팅 구성이 확인됩니다.")

    if lowered_name == "readme.md":
        first_lines = [line.strip("#- *\t ") for line in content.splitlines() if line.strip()]
        if first_lines:
            snippets.append("README에서 프로젝트 소개와 사용 목적 설명이 정리되어 있습니다.")

    if not snippets:
        generic_signals = []
        if "predict" in lowered:
            generic_signals.append("예측 기능")
        if "train" in lowered or "fit(" in lowered:
            generic_signals.append("모델 학습 흐름")
        if "streamlit" in lowered or "react" in lowered:
            generic_signals.append("사용자 화면 구성")
        if "recommend" in lowered or "추천" in lowered:
            generic_signals.append("추천 기능")
        if "chart" in lowered or "plot" in lowered or "matplotlib" in lowered or "seaborn" in lowered:
            generic_signals.append("시각화 구성")
        if generic_signals:
            snippets.append(", ".join(generic_signals) + " 등이 확인됩니다.")

    return " ".join(snippets[:2])
