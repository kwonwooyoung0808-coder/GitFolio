from pathlib import PurePosixPath


def build_prompt(repo_info: dict, my_commits: list, diff_summary: dict, file_contents: dict = {}) -> str:
    commit_summary = "\n".join(
        f"- [{commit['sha'][:7]}] {commit['commit']['message'].splitlines()[0]}"
        for commit in my_commits[:20]
    )
    top_files = "\n".join(
        f"- {item['filename']} ({item['status']}, +{item['additions']}/-{item['deletions']})"
        for item in diff_summary.get("top_files", [])[:8]
    )

    code_fact_section = ""
    if file_contents:
      code_fact_section = "\n\n=== 핵심 파일에서 확인된 구현 사실 ===\n" + _render_code_facts(file_contents)

    return f"""
당신은 한국어 취업용 포트폴리오 문장을 작성하는 전문가입니다.
아래 GitHub 저장소와 커밋 정보를 바탕으로 한국어 자기소개서와 포트폴리오에 바로 붙여 넣을 수 있는 프로젝트 설명을 작성하세요.
반드시 제공된 저장소 정보와 핵심 구현 사실만 바탕으로 작성하세요.
코드에서 확인되지 않은 내용은 추측하지 마세요.
복사용 결과는 이력서 문체에 맞게 간결하고 명확하게 작성하세요.
개발 기간과 팀 규모는 저장소 정보만으로 확정할 수 없으므로 절대 추측하지 마세요.
개발 기간을 알 수 없으면 "직접 입력 필요"라고 작성하세요.
팀 규모를 알 수 없으면 "직접 입력 필요"라고 작성하세요.

반드시 아래 형식을 지켜 주세요.
[프로젝트명]
[개발 기간]
[팀 규모]
[담당 역할]
[주요 구현 내용]
- bullet 3~5개
[사용 기술]
[성과 및 배운 점]

문체 요구사항:
- 과장하지 말고 실제 구현 근거 중심으로 작성
- 파일명 나열보다 기능, 흐름, 구현 목적을 중심으로 작성
- 한국어 이력서와 자소서 문체로 자연스럽게 작성

저장소 정보
- 이름: {repo_info.get('full_name', '')}
- 설명: {repo_info.get('description', '설명 없음')}
- 대표 언어: {repo_info.get('language', '미확인')}
- 스타 수: {repo_info.get('stargazers_count', 0)}

본인 커밋 요약
{commit_summary or '- 커밋 정보 없음'}

주요 변경 파일 요약
{top_files or '- 변경 파일 정보 없음'}{code_fact_section}
"""


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
            snippets.append("사용 라이브러리로 " + ", ".join(dict.fromkeys(packages)) + " 이(가) 확인됩니다.")

    if lowered_name == "package.json":
        packages = []
        for package in ["react", "vite", "next", "axios", "zustand", "tailwindcss"]:
            if package in lowered:
                packages.append("Next.js" if package == "next" else package)
        if packages:
            snippets.append("프론트엔드 구성 요소로 " + ", ".join(dict.fromkeys(packages)) + " 이(가) 확인됩니다.")

    if lowered_name.endswith(".ipynb"):
        if "randomforest" in lowered:
            snippets.append("노트북에서 RandomForest 계열 모델 실험이 확인됩니다.")
        if "xgboost" in lowered:
            snippets.append("노트북에서 XGBoost 모델 실험이 확인됩니다.")
        if "train_test_split" in lowered:
            snippets.append("학습용과 검증용 데이터 분리 흐름이 확인됩니다.")

    if lowered_name in {"app.py", "main.py", "server.py"}:
        if "streamlit" in lowered:
            snippets.append("Streamlit 기반 사용자 입력 및 결과 화면 구성이 확인됩니다.")
        if "fastapi" in lowered:
            snippets.append("FastAPI 엔드포인트 또는 서버 실행 구성이 확인됩니다.")
        if "flask" in lowered:
            snippets.append("Flask 라우팅 또는 서버 실행 구성이 확인됩니다.")
        if "predict" in lowered:
            snippets.append("예측 함수를 통해 입력값 기반 결과를 계산하는 흐름이 확인됩니다.")
        if "classif" in lowered:
            snippets.append("분류 모델을 활용한 결과 판별 로직이 포함되어 있습니다.")
        if "policy" in lowered or "block" in lowered or "filter" in lowered:
            snippets.append("정책 판별 또는 차단 로직이 포함되어 있습니다.")

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
        if "policy" in lowered or "filter" in lowered or "block" in lowered:
            generic_signals.append("정책 기반 판별")
        if generic_signals:
            snippets.append(", ".join(generic_signals) + " 이(가) 확인됩니다.")

    return " ".join(snippets[:2])
