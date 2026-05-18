import { Link } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import Button from './Button'

export default function Header() {
  const { isLoggedIn, loginWithGitHub, logout, user } = useAuth()

  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="text-xl font-bold text-slate-900">
          GitFolio
        </Link>
        <nav className="flex items-center gap-4 text-sm text-slate-600">
          <Link to="/analyze" className="hover:text-slate-900">Analyze</Link>
          <Link to="/history" className="hover:text-slate-900">History</Link>
          {isLoggedIn ? (
            <>
              <span className="hidden text-slate-500 sm:inline">{user?.github_username}</span>
              <Button onClick={logout} className="bg-slate-900 hover:bg-slate-800">Logout</Button>
            </>
          ) : (
            <Button onClick={loginWithGitHub}>GitHub Login</Button>
          )}
        </nav>
      </div>
    </header>
  )
}
