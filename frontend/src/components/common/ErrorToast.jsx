export default function ErrorToast({ message }) {
  if (!message) return null

  return (
    <div className="rounded-[22px] border border-rose-200 bg-rose-50/90 px-5 py-4 text-sm leading-6 text-rose-700 shadow-sm">
      <p className="font-semibold text-rose-900">문제가 발생했습니다</p>
      <p className="mt-1">{message}</p>
    </div>
  )
}
