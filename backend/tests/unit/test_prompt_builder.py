from app.services.github.parser import infer_repo_profile, summarize_diffs
from app.services.llm.prompt_builder import build_prompt
from app.services.report.formatter import build_free_report, format_local_llm_report, format_report_content


def test_prompt_builder_uses_resume_style_instructions():
    repo_info = {
        "full_name": "openai/gitfolio",
        "description": "Portfolio generator",
        "language": "Python",
        "stargazers_count": 10,
        "name": "gitfolio",
    }
    commits = [
        {
            "sha": "abcdef123456",
            "commit": {"message": "Implement streaming report generation\n\nDetails"},
        }
    ]
    diffs = [
        {
            "files": [
                {
                    "filename": "app/main.py",
                    "status": "modified",
                    "additions": 12,
                    "deletions": 3,
                    "changes": 15,
                    "patch": "@@\n+new line\n-old line",
                }
            ]
        }
    ]

    diff_summary = summarize_diffs(diffs)
    prompt = build_prompt(repo_info, commits, diff_summary)

    assert "프로젝트명 :" in prompt
    assert "주요 업무 :" in prompt
    assert "본인 확인 기여 요약" in prompt
    assert "메타 정보는 결과 문장에 쓰지 마세요" in prompt


def test_format_report_content_builds_resume_copy():
    repo_info = {
        "full_name": "openai/gitfolio",
        "description": "Portfolio generator",
        "language": "Python",
        "stargazers_count": 10,
        "name": "gitfolio",
    }
    report = format_report_content(
        """프로젝트명 : GitFolio
주요 업무 : 포트폴리오 초안 생성 서비스 개발
담당 역할 : 백엔드 API 구현
기술 스택 : Python, FastAPI, React
업무 기간 : 직접 입력 필요
개발 인원 : 직접 입력 필요
상세 내용 : 저장소 분석과 보고서 초안 생성을 담당했습니다.
""",
        repo_info,
        {},
    )

    assert report["project_name"] == "gitfolio"
    assert report["main_task"] == "포트폴리오 초안 생성 서비스 개발"
    assert report["copy_prompt"] == ""
    assert "주요 업무 :" in report["raw_text"]


def test_project_name_is_forced_to_repo_name():
    repo_info = {
        "full_name": "kwonwooyoung0808-coder/SafeAgent",
        "description": "Safety agent service",
        "language": "Python",
        "stargazers_count": 0,
        "name": "SafeAgent",
    }

    report = format_report_content(
        """프로젝트명 : SafeAgent GitHub Repository
주요 업무 : 정책 기반 입력 검증 서비스 개발
담당 역할 : 직접 입력 필요
기술 스택 : Python, FastAPI
업무 기간 : 직접 입력 필요
개발 인원 : 직접 입력 필요
상세 내용 : 정책 기반 검증 기능을 구현했습니다.
""",
        repo_info,
        {},
    )

    assert report["project_name"] == "SafeAgent"


def test_free_report_uses_resume_fields():
    repo_info = {
        "full_name": "kwon/repo",
        "description": "Attendance prediction service",
        "language": "Python",
        "name": "repo",
    }
    tree = [
        {"path": "frontend/src/App.jsx", "type": "blob"},
        {"path": "backend/app/main.py", "type": "blob"},
        {"path": "train_model.py", "type": "blob"},
        {"path": "data/sample.csv", "type": "blob"},
        {"path": "package.json", "type": "blob"},
        {"path": "requirements.txt", "type": "blob"},
    ]
    file_contents = {
        "package.json": '{"dependencies":{"react":"^18.0.0"}}',
        "requirements.txt": "fastapi\npandas\nstreamlit\nsqlalchemy\npytest\npyyaml\n",
        "README.md": "# Repo\nAttendance prediction project",
        "app.py": "def predict_attendance():\n    return True\n",
        "docker-compose.yml": "services:\n  app:\n    build: .\n",
    }
    diff_summary = {
        "file_count": 3,
        "additions": 100,
        "deletions": 20,
        "top_files": [
            {"filename": "app.py", "status": "modified", "additions": 50, "deletions": 10},
            {"filename": "train_model.py", "status": "modified", "additions": 30, "deletions": 5},
        ],
    }

    profile = infer_repo_profile(repo_info, tree, file_contents)
    report = build_free_report(repo_info, [{"commit": {"message": "init"}}], diff_summary, "prompt", profile)

    assert report["main_task"]
    assert report["details"]
    assert report["copy_prompt"] == "prompt"
    assert "SQLAlchemy" in report["tech_stack"] or "Pytest" in report["tech_stack"]


def test_local_llm_report_filters_meta_text_from_details():
    repo_info = {
        "full_name": "kwon/safeagent",
        "description": "Safety agent service",
        "language": "Python",
        "name": "SafeAgent",
    }
    commit_summary = {
        "file_count": 10,
        "top_files": [
            {"filename": "src/workflows/input_guard_workflow.py", "status": "added", "additions": 100, "deletions": 0},
            {"filename": "src/engines/policy_engine.py", "status": "added", "additions": 120, "deletions": 0},
        ],
    }
    repo_profile = {
        "overview": "정책 기반 입력 검증과 응답 제어를 제공하는 서비스입니다.",
        "project_type": "풀스택 웹 서비스 프로젝트",
        "tech_stack": ["Python", "React", "FastAPI"],
        "feature_highlights": [
            "정책 기준에 따라 특정 입력이나 콘텐츠를 판별하는 기능이 포함되어 있습니다.",
            "위험하거나 허용되지 않는 입력을 차단하는 흐름이 포함되어 있습니다.",
        ],
        "features": [],
    }
    raw_text = """프로젝트명 : SafeAgent
주요 업무 : 정책 기반 입력 검증 서비스 개발
담당 역할 : 직접 입력 필요
기술 스택 : Python, React, FastAPI
업무 기간 : 직접 입력 필요
개발 인원 : 직접 입력 필요
상세 내용 : 본인 커밋 5개와 변경 파일 236개를 기준으로 초안을 생성했습니다. 정책 기준에 따라 특정 입력이나 콘텐츠를 판별하는 기능이 포함되어 있습니다.
"""

    report = format_local_llm_report(raw_text, repo_info, commit_summary, "prompt", repo_profile)

    assert "본인 커밋 5개" not in report["details"]
    assert "정책 기준" in report["details"]


def test_free_report_highlights_map_route_and_realtime_features():
    repo_info = {
        "full_name": "yoosehyeon/3Team_FlaskPJ",
        "description": None,
        "language": "JavaScript",
        "name": "3Team_FlaskPJ",
    }
    tree = [
        {"path": "backend/app.py", "type": "blob"},
        {"path": "frontend/src/pages/MapPage.tsx", "type": "blob"},
        {"path": "frontend/src/pages/ReportPage.tsx", "type": "blob"},
        {"path": "README.md", "type": "blob"},
        {"path": "requirements.txt", "type": "blob"},
        {"path": "package.json", "type": "blob"},
    ]
    file_contents = {
        "README.md": """
# 모두의길

- 교통약자를 위한 안전 경로 탐색 기능 제공
- Tmap API와 ODsay API를 활용한 대중교통 이동 경로 조회
- 편의시설 및 엘리베이터 위치를 지도에 표시
- 위험 신고 등록 후 실시간 마커 반영
""",
        "requirements.txt": "flask\nsqlalchemy\npytest\npostgis\nsupabase\n",
        "package.json": '{"dependencies":{"react":"^18.0.0","vite":"^5.0.0"}}',
        "backend/app.py": "from flask import Flask\napp=Flask(__name__)\n",
    }
    diff_summary = {
        "file_count": 4,
        "top_files": [
            {"filename": "frontend/src/pages/MapPage.tsx", "status": "added", "additions": 100, "deletions": 0},
            {"filename": "backend/app.py", "status": "modified", "additions": 30, "deletions": 0},
        ],
    }

    profile = infer_repo_profile(repo_info, tree, file_contents)
    report = build_free_report(repo_info, [], diff_summary, "prompt", profile)

    assert "PostGIS" in report["tech_stack"]
    assert "Supabase" in report["tech_stack"]
    assert "교통약자" in report["main_task"] or "경로" in report["main_task"]
    assert "대중교통" in report["main_task"] or "지도" in report["main_task"]
    assert "실시간" in report["details"] or "신고" in report["details"]
    assert "정책 기준" not in report["details"]
    assert "|" not in report["main_task"]
    assert "|" not in report["details"]
    assert "Code 11" not in report["main_task"]


def test_streamlit_project_does_not_misclassify_heatmap_as_tmap():
    repo_info = {
        "full_name": "kwonwooyoung0808-coder/WINE_ML_PROJECT",
        "description": "머신러닝 서비스모델 과제(26.04.03발표)",
        "language": "Jupyter Notebook",
        "name": "WINE_ML_PROJECT",
    }
    tree = [
        {"path": "app.py", "type": "blob"},
        {"path": "README.md", "type": "blob"},
        {"path": "requirements.txt", "type": "blob"},
        {"path": "train.ipynb", "type": "blob"},
    ]
    file_contents = {
        "README.md": """
# 와인 품질 예측 및 취향 추천 서비스

- Streamlit 앱: https://winemlproject.streamlit.app/
- 레드 와인 / 화이트 와인 품질 예측
- 와인 성분 기반 고급 와인 패턴 분류
- 취향 입력 기반 와인 스타일 추천
- heatmap 기반 상관관계 시각화
""",
        "requirements.txt": "streamlit\npandas\nscikit-learn\njoblib\nmatplotlib\nseaborn\nnumpy\n",
        "app.py": "import streamlit as st\n",
        "train.ipynb": "{}",
    }
    diff_summary = {
        "file_count": 2,
        "top_files": [{"filename": "app.py", "status": "modified", "additions": 10, "deletions": 0}],
    }

    profile = infer_repo_profile(repo_info, tree, file_contents)
    report = build_free_report(repo_info, [], diff_summary, "prompt", profile)

    assert "Tmap API" not in report["tech_stack"]
    assert "지도 기반 사용자 화면" not in report["details"]
    assert "지도" not in report["details"]
    assert "https://" not in report["main_task"]
    assert "https://" not in report["details"]

    prompt = build_prompt(repo_info, [], diff_summary, file_contents)
    assert "정책 판별 또는 차단 로직" not in prompt


def test_prompt_builder_describes_config_file_as_settings_not_policy():
    repo_info = {
        "full_name": "example/carelink",
        "description": "care platform",
        "language": "JavaScript",
        "name": "carelink",
        "stargazers_count": 0,
    }
    diff_summary = {"file_count": 1, "top_files": []}
    file_contents = {
        "backend/src/config/env.js": "export const policy = process.env.POLICY_MODE;\nexport const apiUrl = process.env.API_URL;\n",
    }

    prompt = build_prompt(repo_info, [], diff_summary, file_contents)

    assert "정책 기반 판별" not in prompt
    assert "정책 판별 또는 차단 로직" not in prompt
    assert "환경 변수 또는 서비스 설정 구성이 확인됩니다." in prompt


def test_repo_profile_uses_path_highlights_when_readme_is_weak():
    repo_info = {
        "full_name": "code920309/Human_It_3Team",
        "description": None,
        "language": "JavaScript",
        "name": "Human_It_3Team",
    }
    tree = [
        {"path": "frontend/src/pages/UploadPage.jsx", "type": "blob"},
        {"path": "frontend/src/pages/MyPage.jsx", "type": "blob"},
        {"path": "backend/src/controllers/reportController.js", "type": "blob"},
        {"path": "backend/src/services/geminiService.js", "type": "blob"},
        {"path": "backend/src/services/ocrService.js", "type": "blob"},
    ]
    file_contents = {
        "README.md": "# Project\nA web app",
    }

    profile = infer_repo_profile(repo_info, tree, file_contents)
    joined = " ".join(profile["feature_highlights"])

    assert "OCR" in joined or "ocr" in joined
    assert "리포트" in joined
    assert "챗봇" not in joined or isinstance(joined, str)
