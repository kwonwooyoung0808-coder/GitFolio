import { useNavigate } from 'react-router-dom'

export default function BackButton({ fallback = '/', label = '뒤로 가기' }) {
  const navigate = useNavigate()

  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1)
      return
    }
    navigate(fallback)
  }

  return (
    <button
      type="button"
      onClick={handleBack}
      className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
    >
      <span aria-hidden="true">←</span>
      <span>{label}</span>
    </button>
  )
}
