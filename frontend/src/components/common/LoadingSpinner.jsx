export default function LoadingSpinner({ label = '로딩 중...' }) {
  return (
    <div className="section-card flex items-center gap-4">
      <div className="h-10 w-10 animate-spin rounded-full border-[3px] border-sky-100 border-t-sky-600" />
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-700">Loading</p>
        <p className="mt-1 text-slate-600">{label}</p>
      </div>
    </div>
  )
}
