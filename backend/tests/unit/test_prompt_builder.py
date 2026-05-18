from app.services.github.parser import infer_repo_profile, summarize_diffs
from app.services.llm.prompt_builder import build_prompt
from app.services.report.formatter import build_free_report, format_report_content


def test_prompt_builder_and_formatter_produce_portfolio_shape():
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
    report = format_report_content(
        "[project name]\nGitFolio\n[implementation]\n- FastAPI SSE implementation\n[outcome]\nCompleted automated document generation.",
        repo_info,
        diff_summary,
    )

    assert "openai/gitfolio" in prompt
    assert "app/main.py" in prompt
    assert report["project_name"] == "GitFolio"
    assert report["implementation"] == ["FastAPI SSE implementation"]


def test_free_report_uses_repo_structure_to_explain_project():
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
        "requirements.txt": "fastapi\npandas\nstreamlit\n",
        "README.md": "# Repo\nAttendance prediction project",
        "app.py": "def predict_attendance():\n    return True\n",
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

    assert profile["frontend_present"] is True
    assert profile["backend_present"] is True
    assert "풀스택" in report["outcome"] or "풀스택" in report["summary"]
    assert any("프론트엔드" in line or "예측" in line for line in report["implementation"])
