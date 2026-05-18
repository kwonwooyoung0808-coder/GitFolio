import { useEffect, useState } from 'react'

import { fetchReports } from '../api/reportApi'
import BackButton from '../components/common/BackButton'
import ErrorToast from '../components/common/ErrorToast'
import HeaderV2 from '../components/common/HeaderV2'
import LoadingSpinner from '../components/common/LoadingSpinner'
import HistoryList from '../components/report/HistoryList'
import { useAuthV2 } from '../hooks/useAuthV2'

export default function HistoryPageV2() {
  const { token } = useAuthV2()
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchReports(token)
        setReports(data)
      } catch (loadError) {
        setError(loadError.message)
      } finally {
        setLoading(false)
      }
    }

    if (token) load()
  }, [token])

  return (
    <div className="min-h-screen">
      <HeaderV2 />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <BackButton fallback="/" />
          <a
            href="#history-list"
            className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
          >
            목록으로 이동
          </a>
        </div>

        <div className="mb-8 rounded-[28px] border border-slate-200 bg-white/90 px-8 py-8 shadow-[0_20px_50px_-30px_rgba(15,23,42,0.28)]">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">Saved History</p>
          <h1 className="mt-3 text-4xl font-black tracking-[-0.04em] text-slate-950">저장된 분석 이력</h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">
            이전에 만든 초안과 프롬프트를 다시 열어보고, 다운로드 가능한 문서를 확인할 수 있습니다.
          </p>
        </div>

        <div id="history-list">
          {loading ? <LoadingSpinner label="이전 분석 결과를 불러오고 있습니다..." /> : <HistoryList reports={reports} />}
        </div>
        <div className="mt-6">
          <ErrorToast message={error} />
        </div>
      </main>
    </div>
  )
}
