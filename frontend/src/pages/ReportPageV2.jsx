import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { deleteReport, fetchReport, updateReportMeta } from '../api/reportApi'
import BackButton from '../components/common/BackButton'
import ErrorToast from '../components/common/ErrorToast'
import HeaderV2 from '../components/common/HeaderV2'
import LoadingSpinner from '../components/common/LoadingSpinner'
import DownloadButtons from '../components/report/DownloadButtons'
import ReportPreview from '../components/report/ReportPreview'
import { useAuthV2 } from '../hooks/useAuthV2'

export default function ReportPageV2() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { token } = useAuthV2()
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [savingMeta, setSavingMeta] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchReport(id, token)
        setReport(data)
      } catch (loadError) {
        setError(loadError.message)
      } finally {
        setLoading(false)
      }
    }

    if (token) load()
  }, [id, token])

  const handleMetaSave = async (payload) => {
    try {
      setSavingMeta(true)
      const updated = await updateReportMeta(id, payload, token)
      setReport(updated)
      setError('')
    } catch (updateError) {
      setError(updateError.message)
    } finally {
      setSavingMeta(false)
    }
  }

  const handleDelete = async () => {
    if (!report) return
    const confirmed = window.confirm(`"${report.content?.project_name || '이 보고서'}"를 삭제할까요?\n삭제 후에는 복구할 수 없습니다.`)
    if (!confirmed) return

    try {
      setDeleting(true)
      await deleteReport(id, token)
      navigate('/history')
    } catch (deleteError) {
      setError(deleteError.message)
      setDeleting(false)
    }
  }

  return (
    <div className="min-h-screen">
      <HeaderV2 />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <BackButton fallback="/analyze" />
          <button
            type="button"
            onClick={handleDelete}
            disabled={deleting}
            className="inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-4 py-2.5 text-sm font-semibold text-rose-700 transition hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {deleting ? '삭제 중...' : '보고서 삭제'}
          </button>
        </div>

        <div className="mb-8 rounded-[28px] border border-slate-200 bg-white/90 px-8 py-8 shadow-[0_20px_50px_-30px_rgba(15,23,42,0.28)]">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">Saved Report</p>
          <h1 className="mt-3 text-4xl font-black tracking-[-0.04em] text-slate-950">분석 결과 보고서</h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">
            저장소를 분석해 만든 프로젝트 설명 초안입니다. 실제 제출 전에는 프로젝트 맥락에 맞게 기간, 인원, 담당 역할과
            문장을 한 번 더 검토하는 것을 권장합니다.
          </p>
        </div>

        {loading && <LoadingSpinner label="저장된 결과를 불러오고 있습니다..." />}
        <ErrorToast message={error} />

        {report && (
          <div className="space-y-6">
            <div className="rounded-[24px] border border-amber-200 bg-amber-50 px-6 py-5 text-sm leading-7 text-amber-900 shadow-sm">
              <p className="font-bold">초안 사용 안내</p>
              <p className="mt-2">
                이 결과는 자동 생성된 초안입니다. 저장소 구조와 구현 파일을 기준으로 만들지만 프로젝트 설명이나 역할은 직접
                확인해 다듬는 것이 안전합니다.
              </p>
              <p className="mt-2">
                아래 왼쪽 입력 칸에서 <strong>업무 기간</strong>, <strong>개발 인원</strong>, <strong>담당 역할</strong>
                을 수정하면 초안과 외부 AI 전달용 프롬프트에 바로 반영됩니다.
              </p>
            </div>

            <div
              id="report-actions"
              className="glass-panel flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between"
            >
              <div id="report-summary">
                <span className="soft-badge bg-sky-100 text-sky-800">
                  {report.content?.mode === 'local-llm'
                    ? '로컬 LLM 결과'
                    : report.content?.mode === 'cloud-llm'
                      ? '클라우드 LLM 결과'
                      : '규칙 기반 결과'}
                </span>
                <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                  GitFolio가 저장소를 분석해 초안과 복사용 프롬프트를 정리한 상태입니다. 문장 품질을 더 높이고 싶다면 외부
                  AI 전달용 프롬프트를 활용해 다듬을 수 있습니다.
                </p>
              </div>
              <div className="flex flex-col items-end gap-2">
                {savingMeta && <p className="text-xs text-slate-500">수정 내용을 저장하는 중입니다...</p>}
                <DownloadButtons
                  reportId={report.id}
                  token={token}
                  pdfAvailable={report.pdf_available}
                  docxAvailable={report.docx_available}
                />
              </div>
            </div>

            <div id="report-sections">
              <ReportPreview report={report.content} onMetaSave={handleMetaSave} savingMeta={savingMeta} />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
