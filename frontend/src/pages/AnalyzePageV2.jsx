import InputFormV2 from '../components/analyze/InputFormV2'
import BackButton from '../components/common/BackButton'
import HeaderV2 from '../components/common/HeaderV2'

export default function AnalyzePageV2() {
  return (
    <div className="min-h-screen">
      <HeaderV2 />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <BackButton fallback="/" />
          <div className="flex flex-wrap gap-2">
            <a
              href="#analyze-form"
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
            >
              입력 폼
            </a>
            <a
              href="#analyze-guide"
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
            >
              테스트 가이드
            </a>
          </div>
        </div>

        <div className="mb-8 rounded-[28px] border border-slate-200 bg-white/90 px-8 py-8 shadow-[0_20px_50px_-30px_rgba(15,23,42,0.28)]">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">Analyze Repository</p>
          <h1 className="mt-3 text-4xl font-black tracking-[-0.04em] text-slate-950">GitHub 저장소 분석</h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">
            저장소 주소와 GitHub 계정을 넣으면 커밋, 파일 구조, 핵심 코드 내용을 바탕으로 보고서 초안을 생성합니다.
          </p>
        </div>

        <InputFormV2 />
      </main>
    </div>
  )
}
