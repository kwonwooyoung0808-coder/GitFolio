import { Link, useLocation } from 'react-router-dom'

import { useAuthV2 } from '../../hooks/useAuthV2'
import Button from './Button'

const navItems = [
  { to: '/', label: '홈' },
  { to: '/analyze', label: '분석 시작' },
  { to: '/history', label: '저장 이력' },
]

export default function HeaderV2() {
  const location = useLocation()
  const { isLoggedIn, loginWithGitHub, logout, user } = useAuthV2()

  return (
    <header className="sticky top-0 z-30 border-b border-white/60 bg-white/82 backdrop-blur-xl">
      <div className="mx-auto max-w-6xl px-6 py-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center justify-between gap-4">
            <Link to="/" className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-950 text-sm font-black text-white shadow-lg">
                GF
              </div>
              <div>
                <p className="text-lg font-black tracking-[-0.04em] text-slate-950">GitFolio</p>
                <p className="text-xs font-medium uppercase tracking-[0.24em] text-slate-400">Portfolio Draft Lab</p>
              </div>
            </Link>

            {isLoggedIn && (
              <div className="hidden rounded-full border border-slate-200 bg-white px-4 py-2 text-sm text-slate-600 sm:flex sm:items-center sm:gap-2 lg:hidden">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                <span className="font-medium">{user?.github_username}</span>
              </div>
            )}
          </div>

          <div className="flex flex-col gap-3 lg:items-end">
            <nav className="flex flex-wrap gap-2">
              {navItems.map((item) => {
                const active = item.to === '/' ? location.pathname === '/' : location.pathname.startsWith(item.to)
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                      active
                        ? 'bg-sky-100 text-sky-800'
                        : 'border border-slate-200 bg-white text-slate-600 hover:border-sky-200 hover:text-sky-800'
                    }`}
                  >
                    {item.label}
                  </Link>
                )
              })}
            </nav>

            <div className="flex flex-wrap items-center gap-3">
              {isLoggedIn && (
                <div className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm text-slate-600">
                  <span className="font-medium">{user?.github_username}</span>
                </div>
              )}
              {isLoggedIn ? (
                <Button onClick={logout} className="px-4 py-2.5">
                  로그아웃
                </Button>
              ) : (
                <Button onClick={loginWithGitHub} className="px-4 py-2.5">
                  GitHub 로그인
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
