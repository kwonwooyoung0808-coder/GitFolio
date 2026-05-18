import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { fetchReport } from '../api/reportApi'
import BackButton from '../components/common/BackButton'
import ErrorToast from '../components/common/ErrorToast'
import HeaderV2 from '../components/common/HeaderV2'
import LoadingSpinner from '../components/common/LoadingSpinner'
import DownloadButtons from '../components/report/DownloadButtons'
import ReportPreview from '../components/report/ReportPreview'
import { useAuthV2 } from '../hooks/useAuthV2'

export default function ReportPageV2() {
  const { id } = useParams()
  const { token } = useAuthV2()
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

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

  return (
    <div className="min-h-screen">
      <HeaderV2 />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <BackButton fallback="/analyze" />
          <div className="flex flex-wrap gap-2">
            <a
              href="#report-summary"
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
            >
              요약
            </a>
            <a
              href="#report-sections"
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
            >
              본문
            </a>
            <a
              href="#report-actions"
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
            >
              다운로드
            </a>
          </div>
        </div>

        <div className="mb-8 rounded-[28px] border border-slate-200 bg-white/90 px-8 py-8 shadow-[0_20px_50px_-30px_rgba(15,23,42,0.28)]">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">Saved Report</p>
          <h1 className="mt-3 text-4xl font-black tracking-[-0.04em] text-slate-950">분석 결과 보고서</h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">
            저장소를 분석해 만든 프로젝트 설명 초안입니다. 시연용 결과이므로 실제 제출 전에는 사용자가 직접 문장을 검토하고 수정하는 것을 권장합니다.
          </p>
        </div>

        {loading && <LoadingSpinner label="저장된 결과를 불러오고 있습니다..." />}
        <ErrorToast message={error} />

        {report && (
          <div className="space-y-6">
            <div className="rounded-[24px] border border-amber-200 bg-amber-50 px-6 py-5 text-sm leading-7 text-amber-900 shadow-sm">
              <p className="font-bold">무료 버전 안내</p>
              <p className="mt-2">
                이 결과는 자동 생성된 시연용 초안입니다. 저장소 구조와 핵심 파일을 기반으로 만들지만, 프로젝트 설명이나 기능 정리가 완전히 정확하지 않을 수 있습니다.
              </p>
              <p className="mt-2">
                특히 <strong>개발 기간</strong>, <strong>팀 규모</strong>, <strong>담당 역할</strong>은 사용자가 직접 확인해 수정해야 합니다.
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
                  GitFolio가 저장소를 분석해 초안과 복사용 프롬프트를 정리한 상태입니다. 바로 제출하기보다 프로젝트 맥락에 맞게 한 번 더 다듬어 사용하는 것을 권장합니다.
                </p>
              </div>
              <DownloadButtons
                reportId={report.id}
                token={token}
                pdfAvailable={report.pdf_available}
                docxAvailable={report.docx_available}
              />
            </div>

            <div id="report-sections">
              <ReportPreview report={report.content} />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
