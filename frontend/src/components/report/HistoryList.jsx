import { Link } from 'react-router-dom'

function formatSeoulDateTime(value) {
  if (!value) return ''

  const normalizedValue =
    typeof value === 'string' && !/(Z|[+-]\d{2}:\d{2})$/i.test(value)
      ? `${value}Z`
      : value

  return new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(new Date(normalizedValue))
}

export default function HistoryList({ reports, deletingId = null, onDelete }) {
  if (!reports.length) {
    return (
      <div className="section-card text-center">
        <p className="text-lg font-bold tracking-[-0.03em] text-slate-900">아직 저장된 데이터가 없습니다</p>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          분석 시작 화면에서 저장소를 분석하면 결과가 여기에 차곡차곡 저장됩니다.
        </p>
        <Link
          to="/analyze"
          className="mt-5 inline-flex rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          분석 시작으로 이동
        </Link>
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {reports.map((report) => (
        <div
          key={report.id}
          className="section-card transition duration-200 hover:-translate-y-1 hover:border-sky-200 hover:shadow-[0_26px_60px_-34px_rgba(14,165,233,0.35)]"
        >
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <Link to={`/report/${report.id}`} className="min-w-0 flex-1">
              <div className="mb-2">
                <span className="soft-badge bg-slate-100 text-slate-700">Report #{report.id}</span>
              </div>
              <h2 className="text-xl font-bold tracking-[-0.03em] text-slate-950">{report.project_name}</h2>
              <p className="mt-2 text-sm text-slate-500">{report.repo_name}</p>
            </Link>

            <div className="flex items-start gap-3">
              <div className="pt-1 text-sm text-slate-400">{formatSeoulDateTime(report.created_at)}</div>
              <button
                type="button"
                onClick={() => onDelete?.(report)}
                disabled={deletingId === report.id}
                className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-rose-200 bg-rose-50 text-rose-700 transition hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-60"
                aria-label={`${report.project_name} 삭제`}
                title="삭제"
              >
                {deletingId === report.id ? '...' : '🗑'}
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
