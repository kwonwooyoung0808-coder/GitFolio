# GitFolio OAuth / Environment Switch Guide

GitHub OAuth App을 하나만 사용하고 있기 때문에, `로컬 테스트`와 `실배포` 사이를 오갈 때 URL 값을 맞춰줘야 한다.

## 1. 로컬 테스트용

### GitHub OAuth App

- `Homepage URL`
  - `http://localhost:5173`
- `Authorization callback URL`
  - `http://127.0.0.1:8000/api/v1/auth/github/callback`

### backend/.env

```env
GITHUB_REDIRECT_URI=http://127.0.0.1:8000/api/v1/auth/github/callback
FRONTEND_URL=http://localhost:5173
JWT_SECRET=gitfolio-local-2026-J7mQ2xLp9Rs4Tv8Wy1Nc6Kd3Hb5ZaE
```

### 로컬 테스트 순서

1. GitHub OAuth App URL을 로컬용으로 변경
2. `backend/.env`가 로컬용 값인지 확인
3. 백엔드 실행
   - `uvicorn app.main:app --reload`
4. 프론트 실행
5. GitHub 로그인
6. 저장소 분석 테스트

## 2. 배포용

### GitHub OAuth App

- `Homepage URL`
  - `https://gitfolio-frontend.netlify.app`
- `Authorization callback URL`
  - `https://gitfolio-uojk.onrender.com/api/v1/auth/github/callback`

### Render Environment Variables

```env
GITHUB_REDIRECT_URI=https://gitfolio-uojk.onrender.com/api/v1/auth/github/callback
FRONTEND_URL=https://gitfolio-frontend.netlify.app
JWT_SECRET=gitfolio-local-2026-J7mQ2xLp9Rs4Tv8Wy1Nc6Kd3Hb5ZaE
```

### 배포 반영 순서

1. 로컬 수정사항 확인
2. `git add` / `commit` / `push`
3. GitHub OAuth App URL을 배포용으로 다시 변경
4. Render 환경변수가 배포용 값인지 확인
5. Render 재배포 또는 자동 재배포 확인
6. Netlify에서 로그인 / 분석 / DOCX 다운로드 테스트

## 3. 중요한 구분

- `backend/.env`
  - 로컬 실행할 때만 사용
- Render 환경변수
  - 배포 백엔드에서만 사용
- GitHub OAuth App URL
  - 현재 로그인 흐름을 어느 환경으로 보낼지 결정

즉, 배포할 때는 보통 `VSCode의 .env`는 건드릴 필요가 없고, `GitHub OAuth App URL`과 `Render 환경변수`만 배포용으로 맞추면 된다.

## 4. 왜 401 또는 Invalid Redirect URI가 뜨는가

### `Invalid Redirect URI`

로컬 백엔드가 GitHub에 보내는 `redirect_uri`와 GitHub OAuth App에 등록된 callback URL이 다를 때 발생한다.

### `401 Unauthorized`

브라우저에 저장된 토큰이 현재 백엔드의 `JWT_SECRET` 기준과 맞지 않거나, 로컬/배포 토큰을 섞어 쓸 때 발생할 수 있다.

## 5. 권장 개선안

가장 깔끔한 방법은 GitHub OAuth App을 2개로 분리하는 것이다.

- 로컬용 OAuth App
- 배포용 OAuth App

이렇게 나누면 매번 URL을 바꿔 끼울 필요가 없다.
