import { BrowserRouter, Route, Routes } from 'react-router-dom'

import AnalyzePage from './pages/AnalyzePageV2'
import HistoryPage from './pages/HistoryPageV2'
import HomePage from './pages/HomePageV2'
import ReportPage from './pages/ReportPageV2'

export default function App() {
  return (
    <div className="app-shell">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/report/:id" element={<ReportPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}

function AuthCallback() {
  const params = new URLSearchParams(window.location.search)
  const token = params.get('token')

  if (token) {
    localStorage.setItem('gitfolio_token', token)
    window.location.href = '/analyze'
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl items-center justify-center px-6">
      <div className="glass-panel w-full p-10 text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">GitHub OAuth</p>
        <h1 className="mt-4 text-3xl font-bold tracking-[-0.03em] text-slate-900">로그인 정보를 처리하고 있습니다</h1>
        <p className="mt-3 text-slate-600">잠시만 기다리면 분석 화면으로 자동 이동합니다.</p>
      </div>
    </div>
  )
}
