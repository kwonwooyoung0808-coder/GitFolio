import { useEffect, useState } from 'react'

import Button from '../common/Button'

const sectionLinks = [
  { href: '#section-main-task', label: '주요 업무' },
  { href: '#section-tech', label: '기술 스택' },
  { href: '#section-details', label: '상세 내용' },
  { href: '#section-draft', label: '이력서용 초안' },
  { href: '#section-prompt', label: '외부 AI 전달용 프롬프트' },
]

export default function ReportPreview({ report, onMetaSave, savingMeta = false }) {
  if (!report) return null

  const [period, setPeriod] = useState(toEditableValue(report.period))
  const [scale, setScale] = useState(toEditableValue(report.scale))
  const [role, setRole] = useState(toEditableValue(report.role))

  useEffect(() => {
    setPeriod(toEditableValue(report.period))
    setScale(toEditableValue(report.scale))
    setRole(toEditableValue(report.role))
  }, [report.period, report.scale, report.role])

  const copyDraft = async () => {
    if (!report.raw_text) return
    await navigator.clipboard.writeText(report.raw_text)
  }

  const copyPrompt = async () => {
    if (!report.copy_prompt) return
    await navigator.clipboard.writeText(report.copy_prompt)
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
      <aside className="space-y-6 lg:sticky lg:top-28 lg:self-start">
        <div className="section-card">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">Report Menu</p>
          <div className="mt-4 grid gap-2">
            {sectionLinks.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
              >
                {item.label}
              </a>
            ))}
          </div>
        </div>

        <div className="section-card border-amber-200 bg-amber-50">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-amber-800">Check Before Use</p>
          <ul className="mt-3 space-y-2 text-sm leading-6 text-amber-900">
            <li>업무 기간은 실제 일정에 맞게 직접 입력해야 합니다.</li>
            <li>개발 인원과 담당 역할도 실제 프로젝트 기준으로 수정해야 합니다.</li>
            <li>상세 내용은 제출 전 한 번 더 다듬어 프로젝트 맥락에 맞추는 것을 권장합니다.</li>
          </ul>
        </div>

        <div id="section-overview" className="section-card anchor-offset">
          <div className="mb-4 flex flex-wrap gap-2">
            <span className="soft-badge bg-emerald-100 text-emerald-800">
              {report.mode === 'free' ? '규칙 기반 초안' : report.mode === 'local-llm' ? '로컬 LLM 초안' : '클라우드 LLM 초안'}
            </span>
            {report.repo?.full_name && (
              <span className="soft-badge max-w-full break-all whitespace-normal bg-slate-100 text-slate-700">
                {report.repo.full_name}
              </span>
            )}
          </div>
          <h2 className="break-all text-3xl font-black tracking-[-0.04em] text-slate-950">{report.project_name}</h2>
        </div>

        <EditableInfoCard title="업무 기간" value={period} placeholder="예: 2026.04 ~ 2026.05" onChange={setPeriod} />
        <EditableInfoCard title="개발 인원" value={scale} placeholder="예: 1명 / 6명 / 개인 프로젝트" onChange={setScale} />
        <EditableInfoCard
          title="담당 역할"
          value={role}
          placeholder="예: OCR 분석 기능 구현, 결과 저장 API 개발"
          multiline
          onChange={setRole}
        />
        <Button
          className="w-full px-4 py-3"
          onClick={() => onMetaSave?.({ period, scale, role })}
          disabled={savingMeta}
        >
          {savingMeta ? '수정 반영 중...' : '수정 반영'}
        </Button>
      </aside>

      <section className="space-y-6">
        <div id="section-main-task" className="section-card anchor-offset">
          <h3 className="section-title">주요 업무</h3>
          <p className="mt-4 text-sm leading-7 text-slate-700">{report.main_task}</p>
        </div>

        <div id="section-tech" className="section-card anchor-offset">
          <h3 className="section-title">기술 스택</h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {(report.tech_stack || []).map((item) => (
              <span key={item} className="rounded-full bg-sky-50 px-3 py-1.5 text-sm font-medium text-sky-800">
                {item}
              </span>
            ))}
          </div>
        </div>

        <div id="section-details" className="anchor-offset">
          <InfoCard title="상세 내용" value={report.details || report.outcome} multiline />
        </div>

        {report.raw_text && (
          <div id="section-draft" className="section-card anchor-offset">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h3 className="section-title">이력서용 초안</h3>
              <Button onClick={copyDraft} className="bg-slate-950 px-4 py-2.5 hover:bg-slate-800">
                복사하기
              </Button>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap rounded-[20px] bg-slate-950 p-5 text-sm leading-7 text-slate-100">
              {report.raw_text}
            </pre>
          </div>
        )}

        {report.copy_prompt && (
          <div id="section-prompt" className="section-card anchor-offset">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 className="section-title">외부 AI 전달용 프롬프트</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  이력서용 초안을 더 자연스럽게 다듬고 싶을 때 ChatGPT, Claude 같은 외부 AI에 붙여 넣는 입력문입니다.
                  이력서에 직접 제출하는 내용이 아니라, 외부 AI에게 재작성이나 문장 보완을 요청할 때 사용합니다.
                </p>
              </div>
              <Button onClick={copyPrompt} className="bg-sky-700 px-4 py-2.5 hover:bg-sky-800">
                프롬프트 복사
              </Button>
            </div>
            <pre className="max-h-[32rem] overflow-auto whitespace-pre-wrap rounded-[20px] border border-slate-200 bg-slate-50 p-5 text-sm leading-7 text-slate-700">
              {report.copy_prompt}
            </pre>
          </div>
        )}

        {!!report.manual_steps?.length && (
          <div className="section-card">
            <h3 className="section-title">사용 팁</h3>
            <ol className="mt-4 space-y-3">
              {report.manual_steps.map((step, index) => (
                <li key={step} className="flex gap-3 text-sm leading-7 text-slate-700">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-sky-100 text-xs font-bold text-sky-800">
                    {index + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>
        )}
      </section>
    </div>
  )
}

function InfoCard({ title, value, multiline = false }) {
  return (
    <div className="section-card">
      <h3 className="section-title">{title}</h3>
      <p className={`mt-3 text-sm leading-7 text-slate-700 ${multiline ? 'whitespace-pre-wrap' : ''}`}>{value}</p>
    </div>
  )
}

function EditableInfoCard({ title, value, onChange, placeholder = '', multiline = false }) {
  return (
    <div className="section-card">
      <h3 className="section-title">{title}</h3>
      {multiline ? (
        <textarea
          className="mt-3 min-h-[120px] w-full resize-y rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-7 text-slate-700 focus:border-sky-300 focus:outline-none focus:ring-4 focus:ring-sky-100"
          value={value || ''}
          placeholder={placeholder}
          onChange={(event) => onChange?.(event.target.value)}
        />
      ) : (
        <input
          className="mt-3 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-7 text-slate-700 focus:border-sky-300 focus:outline-none focus:ring-4 focus:ring-sky-100"
          value={value || ''}
          placeholder={placeholder}
          onChange={(event) => onChange?.(event.target.value)}
        />
      )}
    </div>
  )
}

function toEditableValue(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  if (text.includes('직접 입력')) return ''
  if (text.includes('실제 프로젝트 진행 기간')) return ''
  if (text.includes('팀 프로젝트인지 개인 프로젝트인지')) return ''
  if (text.includes('실제 맡은 역할')) return ''
  return text
}
