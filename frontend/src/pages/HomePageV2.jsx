import { Link } from 'react-router-dom'

import Button from '../components/common/Button'
import HeaderV2 from '../components/common/HeaderV2'
import { useAuthV2 } from '../hooks/useAuthV2'

const steps = [
  'GitHub 로그인 후 분석할 저장소 주소를 입력합니다.',
  '커밋 이력, 파일 구조, 핵심 파일 내용을 바탕으로 초안을 만듭니다.',
  '결과 화면에서 초안, 복사용 프롬프트, DOCX 다운로드를 확인합니다.',
]

export default function HomePageV2() {
  const { isLoggedIn, loginWithGitHub } = useAuthV2()

  return (
    <div className="min-h-screen">
      <HeaderV2 />
      <main className="mx-auto max-w-6xl px-6 py-10 md:py-16">
        <section className="glass-panel overflow-hidden">
          <div className="grid gap-10 px-8 py-10 md:px-12 md:py-14 lg:grid-cols-[1.2fr_0.8fr]">
            <div>
              <p className="soft-badge bg-sky-100 text-sky-800">무료 테스트 모드</p>
              <h1 className="mt-6 text-4xl font-black leading-tight tracking-[-0.05em] text-slate-950 md:text-6xl">
                GitHub 저장소를 넣고
                <br />
                프로젝트 설명 초안까지
                <br />
                한 번에 정리합니다
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
                GitFolio는 커밋만 나열하지 않고, 저장소 구조와 핵심 코드 내용을 함께 읽어 포트폴리오용 보고서 초안을 만들어 주는 도구입니다.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                {isLoggedIn ? (
                  <Link to="/analyze">
                    <Button className="px-7 py-3.5">분석 화면으로 이동</Button>
                  </Link>
                ) : (
                  <Button onClick={loginWithGitHub} className="px-7 py-3.5">
                    GitHub 로그인
                  </Button>
                )}
                <Link
                  to="/history"
                  className="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-7 py-3.5 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
                >
                  저장된 결과 보기
                </Link>
              </div>
            </div>

            <div className="section-card border-slate-100 bg-slate-950 text-white">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-300">빠른 이동 메뉴</p>
              <div className="mt-5 grid gap-3">
                <Link to="/analyze" className="rounded-2xl border border-white/10 bg-white/5 px-5 py-4 transition hover:bg-white/10">
                  <p className="font-semibold">저장소 분석 시작</p>
                  <p className="mt-1 text-sm text-slate-300">저장소 주소를 입력하고 실시간 진행 상태를 확인합니다.</p>
                </Link>
                <Link to="/history" className="rounded-2xl border border-white/10 bg-white/5 px-5 py-4 transition hover:bg-white/10">
                  <p className="font-semibold">저장된 이력 보기</p>
                  <p className="mt-1 text-sm text-slate-300">이전에 만든 초안과 프롬프트를 다시 열어봅니다.</p>
                </Link>
              </div>

              <ol className="mt-8 space-y-4">
                {steps.map((step, index) => (
                  <li key={step} className="flex gap-3">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/10 text-sm font-bold text-white">
                      {index + 1}
                    </span>
                    <p className="text-sm leading-7 text-slate-200">{step}</p>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
