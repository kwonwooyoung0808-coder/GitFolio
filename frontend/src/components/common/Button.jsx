export default function Button({ children, className = '', ...props }) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_14px_30px_-18px_rgba(15,23,42,0.9)] transition duration-200 hover:-translate-y-0.5 hover:bg-sky-700 focus:outline-none focus:ring-4 focus:ring-sky-100 disabled:cursor-not-allowed disabled:translate-y-0 disabled:bg-slate-300 disabled:text-slate-100 ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
