import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { deleteReport, fetchReports } from '../api/reportApi'
import BackButton from '../components/common/BackButton'
import ErrorToast from '../components/common/ErrorToast'
import HeaderV2 from '../components/common/HeaderV2'
import LoadingSpinner from '../components/common/LoadingSpinner'
import HistoryList from '../components/report/HistoryList'
import { useAuthV2 } from '../hooks/useAuthV2'

export default function HistoryPageV2() {
  const { token, loginWithGitHub, isLoggedIn } = useAuthV2()
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchReports(token)
        setReports(data)
      } catch (loadError) {
        setError(loadError.message || '저장 이력을 불러오지 못했습니다.')
      } finally {
        setLoading(false)
      }
    }

    if (!token) {
      setLoading(false)
      setReports([])
      setError('')
      return
    }

    load()
  }, [token])

  const handleDelete = async (report) => {
    const confirmed = window.confirm(`"${report.project_name}" 보고서를 삭제할까요?\n삭제 후에는 복구할 수 없습니다.`)
    if (!confirmed) return

    try {
      setDeletingId(report.id)
      await deleteReport(report.id, token)
      setReports((prev) => prev.filter((item) => item.id !== report.id))
      setError('')
    } catch (deleteError) {
      setError(deleteError.message || '보고서를 삭제하지 못했습니다.')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="min-h-screen">
      <HeaderV2 />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <BackButton fallback="/" />
        </div>

        <div className="mb-8 rounded-[28px] border border-slate-200 bg-white/90 px-8 py-8 shadow-[0_20px_50px_-30px_rgba(15,23,42,0.28)]">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">Saved History</p>
          <h1 className="mt-3 text-4xl font-black tracking-[-0.04em] text-slate-950">저장된 분석 이력</h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">
            이전에 만든 초안과 프롬프트를 다시 확인하고, 저장된 결과 문서를 이어서 검토할 수 있습니다.
          </p>
        </div>

        {!isLoggedIn ? (
          <div className="section-card text-center" id="history-list">
            <p className="text-lg font-bold tracking-[-0.03em] text-slate-900">로그인이 필요합니다.</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              저장 이력은 로그인한 사용자 기준으로 불러옵니다. GitHub 로그인 후 바로 확인해보세요.
            </p>
            <button
              type="button"
              onClick={loginWithGitHub}
              className="mt-5 inline-flex rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              GitHub 로그인
            </button>
          </div>
        ) : loading ? (
          <div id="history-list">
            <LoadingSpinner label="이전 분석 결과를 불러오고 있습니다..." />
          </div>
        ) : (
          <div id="history-list">
            <HistoryList reports={reports} deletingId={deletingId} onDelete={handleDelete} />
          </div>
        )}

        {error ? (
          <div className="mt-6">
            <ErrorToast message={error} />
          </div>
        ) : null}

        {!isLoggedIn ? (
          <div className="mt-6 text-center">
            <Link to="/" className="text-sm font-semibold text-slate-500 transition hover:text-slate-700">
              홈으로 이동
            </Link>
          </div>
        ) : null}
      </main>
    </div>
  )
}
