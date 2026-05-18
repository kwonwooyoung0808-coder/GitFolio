import Button from '../common/Button'

const sectionLinks = [
  { href: '#section-overview', label: '프로젝트 개요' },
  { href: '#section-implementation', label: '주요 구현 내용' },
  { href: '#section-tech', label: '사용 기술' },
  { href: '#section-outcome', label: '성과 및 배운 점' },
  { href: '#section-draft', label: '초안' },
  { href: '#section-prompt', label: '복사용 프롬프트' },
]

export default function ReportPreview({ report }) {
  if (!report) return null

  const copyPrompt = async () => {
    if (!report.copy_prompt) return
    await navigator.clipboard.writeText(report.copy_prompt)
  }

  const copyDraft = async () => {
    if (!report.raw_text) return
    await navigator.clipboard.writeText(report.raw_text)
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
            <li>개발 기간은 실제 일정에 맞게 직접 입력해야 합니다.</li>
            <li>팀 규모와 담당 역할도 실제 프로젝트 기준으로 수정해야 합니다.</li>
            <li>주요 구현 내용과 성과 문장은 최종 제출 전에 한 번 더 검토하는 것을 권장합니다.</li>
          </ul>
        </div>

        <div id="section-overview" className="section-card">
          <div className="mb-4 flex flex-wrap gap-2">
            <span className="soft-badge bg-emerald-100 text-emerald-800">
              {report.mode === 'free' ? '규칙 기반 초안' : report.mode === 'local-llm' ? '로컬 LLM 초안' : '클라우드 LLM 초안'}
            </span>
            {report.repo?.full_name && <span className="soft-badge bg-slate-100 text-slate-700">{report.repo.full_name}</span>}
          </div>
          <h2 className="text-3xl font-black tracking-[-0.04em] text-slate-950">{report.project_name}</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            {report.repo?.description || '저장소 설명이 비어 있어 커밋, 파일 구조, 핵심 코드 내용을 바탕으로 초안을 정리했습니다.'}
          </p>
        </div>

        <InfoCard title="개발 기간" value={report.period} />
        <InfoCard title="팀 규모" value={report.scale} />
        <InfoCard title="담당 역할" value={report.role} />
      </aside>

      <section className="space-y-6">
        <div id="section-implementation" className="section-card">
          <h3 className="section-title">주요 구현 내용</h3>
          <ul className="mt-4 space-y-3">
            {(report.implementation || []).map((item, index) => (
              <li
                key={`${item}-${index}`}
                className="rounded-[18px] border border-slate-200 bg-slate-50/80 px-4 py-3 text-sm leading-7 text-slate-700"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div id="section-tech" className="section-card">
          <h3 className="section-title">사용 기술</h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {(report.tech_stack || []).map((item) => (
              <span key={item} className="rounded-full bg-sky-50 px-3 py-1.5 text-sm font-medium text-sky-800">
                {item}
              </span>
            ))}
          </div>
        </div>

        <div id="section-outcome">
          <InfoCard title="성과 및 배운 점" value={report.outcome} multiline />
        </div>

        {report.raw_text && (
          <div id="section-draft" className="section-card">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h3 className="section-title">초안</h3>
              <Button onClick={copyDraft} className="bg-slate-950 px-4 py-2.5 hover:bg-slate-800">
                초안 복사
              </Button>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap rounded-[20px] bg-slate-950 p-5 text-sm leading-7 text-slate-100">
              {report.raw_text}
            </pre>
          </div>
        )}

        {report.copy_prompt && (
          <div id="section-prompt" className="section-card">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h3 className="section-title">복사용 프롬프트</h3>
              <Button onClick={copyPrompt} className="bg-sky-700 px-4 py-2.5 hover:bg-sky-800">
                프롬프트 복사
              </Button>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap rounded-[20px] border border-slate-200 bg-slate-50 p-5 text-sm leading-7 text-slate-700">
              {report.copy_prompt}
            </pre>
          </div>
        )}

        {!!report.manual_steps?.length && (
          <div className="section-card">
            <h3 className="section-title">무료 모드 사용 방법</h3>
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
