export function useAuthV2() {
  const token = localStorage.getItem('gitfolio_token')
  let user = null

  if (token) {
    try {
      const payload = token.split('.')[1]
      user = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    } catch (_) {
      user = null
    }
  }

  const loginWithGitHub = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/github`
  }

  const logout = () => {
    localStorage.removeItem('gitfolio_token')
    window.location.href = '/'
  }

  return { token, user, loginWithGitHub, logout, isLoggedIn: Boolean(token) }
}
