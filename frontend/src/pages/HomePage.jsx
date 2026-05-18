import { useAuth } from '../hooks/useAuth'

export default function HomePage() {
  const { loginWithGitHub, isLoggedIn } = useAuth()
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-white">
      <h1 className="text-5xl font-bold text-blue-700 mb-4">GitFolio</h1>
      <p className="text-gray-500 mb-8 text-lg">GitHub 레포를 취업 포트폴리오로 자동 변환</p>
      {isLoggedIn
        ? <a href="/analyze" className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700">분석 시작</a>
        : <button onClick={loginWithGitHub} className="bg-gray-900 text-white px-8 py-3 rounded-lg hover:bg-gray-800">
            GitHub으로 로그인
          </button>
      }
    </div>
  )
}
