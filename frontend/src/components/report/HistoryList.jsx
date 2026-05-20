import { Link } from 'react-router-dom'

export default function HistoryList({ reports }) {
  if (!reports.length) {
    return (
      <div className="section-card text-center">
        <p className="text-lg font-bold tracking-[-0.03em] text-slate-900">아직 저장된 데이터가 없습니다</p>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          분석 시작 화면에서 저장소를 분석하면 결과가 이곳에 저장됩니다.
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
        <Link
          key={report.id}
          to={`/report/${report.id}`}
          className="section-card transition duration-200 hover:-translate-y-1 hover:border-sky-200 hover:shadow-[0_26px_60px_-34px_rgba(14,165,233,0.35)]"
        >
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="mb-2">
                <span className="soft-badge bg-slate-100 text-slate-700">Report #{report.id}</span>
              </div>
              <h2 className="text-xl font-bold tracking-[-0.03em] text-slate-950">{report.project_name}</h2>
              <p className="mt-2 text-sm text-slate-500">{report.repo_name}</p>
            </div>
            <div className="text-sm text-slate-400">{new Date(report.created_at).toLocaleString()}</div>
          </div>
        </Link>
      ))}
    </div>
  )
}
