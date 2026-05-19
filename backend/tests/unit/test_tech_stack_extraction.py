from app.services.github.parser import infer_repo_profile


def test_readme_tech_stack_is_prioritized_and_javascript_dropped_when_typescript_exists():
    repo_info = {
        "full_name": "code920309/Human_It_3Team",
        "description": None,
        "language": "JavaScript",
        "name": "Human_It_3Team",
    }
    tree = [
        {"path": "README.md", "type": "blob"},
        {"path": "frontend/package.json", "type": "blob"},
        {"path": "backend/package.json", "type": "blob"},
    ]
    file_contents = {
        "README.md": """
# Human_It_3Team

## 기술 스택

### Frontend
- React v19 (Vite v6)
- TypeScript v5.8
- Tailwind CSS v4
- React Router DOM v7
- Axios
- Framer Motion
- Recharts
- Swiper
- Lucide React
- React Markdown
- Gemini API (@google/genai)

### Backend
- Node.js v20 / Express v5
- MySQL / PostgreSQL (pg)
- Supabase
- Gemini API (@google/generative-ai)
- JWT (jsonwebtoken)
- bcryptjs
- Multer
- CORS / cookie-parser
- serverless-http
""",
        "frontend/package.json": '{"dependencies":{"react":"^19.0.0","vite":"^6.0.0","axios":"^1.0.0","framer-motion":"^12.0.0","recharts":"^3.0.0","swiper":"^12.0.0","lucide-react":"^1.0.0","react-markdown":"^10.0.0"}}',
        "backend/package.json": '{"dependencies":{"express":"^5.0.0","jsonwebtoken":"^9.0.0","bcryptjs":"^2.4.3","multer":"^1.4.5","cors":"^2.8.5","cookie-parser":"^1.4.7","serverless-http":"^3.2.0","pg":"^8.0.0","@google/generative-ai":"^0.0.0"}}',
    }

    profile = infer_repo_profile(repo_info, tree, file_contents)

    assert "JavaScript" not in profile["tech_stack"]
    assert "TypeScript" in profile["tech_stack"]
    assert "Node.js" in profile["tech_stack"]
    assert "Express" in profile["tech_stack"]
    assert "Gemini API" in profile["tech_stack"]
    assert "MySQL" in profile["tech_stack"]
    assert "PostgreSQL" in profile["tech_stack"]
    assert "Supabase" in profile["tech_stack"]
    assert "Axios" not in profile["tech_stack"]
    assert "serverless-http" not in profile["tech_stack"]


def test_tech_stack_falls_back_to_manifests_paths_and_code_when_readme_is_missing():
    repo_info = {
        "full_name": "example/no-readme-project",
        "description": None,
        "language": "JavaScript",
        "name": "no-readme-project",
    }
    tree = [
        {"path": "frontend/package.json", "type": "blob"},
        {"path": "frontend/tsconfig.json", "type": "blob"},
        {"path": "frontend/vite.config.ts", "type": "blob"},
        {"path": "frontend/src/App.tsx", "type": "blob"},
        {"path": "backend/package.json", "type": "blob"},
        {"path": "backend/src/server.js", "type": "blob"},
        {"path": "backend/src/routes/auth.js", "type": "blob"},
    ]
    file_contents = {
        "frontend/package.json": '{"dependencies":{"react":"^19.0.0","vite":"^6.0.0","axios":"^1.0.0","tailwindcss":"^4.0.0"}}',
        "frontend/src/App.tsx": 'import React from "react";\nimport axios from "axios";\n',
        "backend/package.json": '{"dependencies":{"express":"^5.0.0","jsonwebtoken":"^9.0.0","cors":"^2.8.5"}}',
        "backend/src/server.js": 'const express = require("express");\nconst cors = require("cors");\n',
    }

    profile = infer_repo_profile(repo_info, tree, file_contents)

    assert "TypeScript" in profile["tech_stack"]
    assert "React" in profile["tech_stack"]
    assert "Vite" in profile["tech_stack"]
    assert "Tailwind CSS" in profile["tech_stack"]
    assert "Node.js" in profile["tech_stack"]
    assert "Express" in profile["tech_stack"]
    assert "JWT" in profile["tech_stack"]
    assert "Axios" not in profile["tech_stack"]
    assert "CORS" not in profile["tech_stack"]
    assert "JavaScript" not in profile["tech_stack"]
