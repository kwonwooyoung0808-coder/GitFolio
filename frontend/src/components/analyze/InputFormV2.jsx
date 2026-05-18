import { useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

import { getAnalyzeStreamUrl } from '../../api/analyzeApi'
import { useAnalyzeStream } from '../../hooks/useAnalyzeStream'
import { useAuthV2 } from '../../hooks/useAuthV2'
import Button from '../common/Button'
import ErrorToast from '../common/ErrorToast'

const guideItems = [
  '본인 커밋이 실제로 있는 공개 저장소부터 테스트하면 결과 확인이 쉽습니다.',
  '분석 중에는 커밋 수집, 핵심 파일 읽기, 초안 생성 순서로 상태가 바뀝니다.',
  '완료되면 결과 페이지로 자동 이동하며 초안과 DOCX 다운로드를 볼 수 있습니다.',
]

export default function InputFormV2() {
  const navigate = useNavigate()
  const { token, user } = useAuthV2()
  const { repoUrl, githubIdentity, setGithubIdentity, setRepoUrl, status, content, result, error, isDone, startStream } =
    useAnalyzeStream()

  useEffect(() => {
    if (user?.github_username && !githubIdentity) {
      setGithubIdentity(user.github_username)
    }
  }, [githubIdentity, setGithubIdentity, user])

  useEffect(() => {
    if (isDone && result?.report_id) {
      navigate(`/report/${result.report_id}`)
    }
  }, [isDone, navigate, result])

  const canSubmit = !!repoUrl && !!token
  const progressTone = useMemo(() => {
    if (error) return 'bg-rose-50 text-rose-700 border-rose-200'
    if (status) return 'bg-sky-50 text-sky-800 border-sky-200'
    return 'bg-slate-50 text-slate-600 border-slate-200'
  }, [error, status])

  const handleSubmit = async () => {
    try {
      await startStream(getAnalyzeStreamUrl(), { repo_url: repoUrl, github_identity: githubIdentity }, token)
    } catch (streamError) {
      console.error(streamError)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.12fr_0.88fr]">
      <section id="analyze-form" className="glass-panel p-7 md:p-8">
        <div className="mb-7 flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">Input Form</p>
            <h2 className="mt-3 text-2xl font-black tracking-[-0.03em] text-slate-950">저장소 입력</h2>
          </div>
          <span className="soft-badge bg-amber-100 text-amber-800">무료 모드</span>
        </div>

        <div className="space-y-4">
          <label className="field-shell block">
            <span className="field-label">Repository URL</span>
            <input
              className="field-input"
              placeholder="예: https://github.com/owner/repo"
              value={repoUrl}
              onChange={(event) => setRepoUrl(event.target.value)}
            />
          </label>

          <label className="field-shell block">
            <span className="field-label">GitHub Username</span>
            <input
              className="field-input"
              placeholder="본인 GitHub username 또는 numeric id"
              value={githubIdentity}
              onChange={(event) => setGithubIdentity(event.target.value)}
            />
          </label>
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Button className="min-w-[180px] px-6 py-3.5" onClick={handleSubmit} disabled={!canSubmit}>
            무료 초안 생성
          </Button>
          {!token && <span className="text-sm text-slate-500">GitHub 로그인 후 분석 버튼이 활성화됩니다.</span>}
        </div>

        <div className={`mt-6 rounded-[22px] border px-5 py-4 ${progressTone}`}>
          <p className="text-xs font-semibold uppercase tracking-[0.22em]">현재 상태</p>
          <p className="mt-2 text-sm leading-6">{error || status || '아직 분석을 시작하지 않았습니다.'}</p>
        </div>

        {content && (
          <div className="mt-5 rounded-[24px] border border-slate-200 bg-slate-950 p-5 text-sm leading-7 text-slate-100 shadow-lg">
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.22em] text-sky-300">실시간 출력</p>
            <div className="whitespace-pre-wrap">{content}</div>
          </div>
        )}

        <div className="mt-5">
          <ErrorToast message={error} />
        </div>
      </section>

      <aside id="analyze-guide" className="space-y-6">
        <section className="section-card">
          <h3 className="section-title">테스트 가이드</h3>
          <ol className="mt-4 space-y-4">
            {guideItems.map((item, index) => (
              <li key={item} className="flex gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sky-100 text-sm font-bold text-sky-800">
                  {index + 1}
                </span>
                <p className="text-sm leading-7 text-slate-700">{item}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className="section-card">
          <h3 className="section-title">화면 이동 메뉴</h3>
          <div className="mt-4 grid gap-3">
            <a
              href="#analyze-form"
              className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
            >
              입력 폼으로 이동
            </a>
            <a
              href="#analyze-guide"
              className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-800"
            >
              가이드 다시 보기
            </a>
          </div>
        </section>
      </aside>
    </div>
  )
}
