# GitFolio

GitHub URL 기반 취업용 포트폴리오 자동 생성 서비스

## 빠른 시작

### 백엔드
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # .env 파일 작성
uvicorn app.main:app --reload
```

### 프론트엔드
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## 기술 스택
- Backend: FastAPI + PostgreSQL + SQLAlchemy
- LLM: Claude claude-sonnet-4-5 (Anthropic API) — SSE 스트리밍
- Frontend: React + Vite + Tailwind CSS
- Deploy: Render (Backend) + Netlify (Frontend)
