import { useAuthStore } from '../store/authStore'

export function useAuth() {
  const { token, user, setToken, clearAuth } = useAuthStore()

  const loginWithGitHub = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/github`
  }

  const logout = () => clearAuth()

  return { token, user, loginWithGitHub, logout, isLoggedIn: !!token }
}
