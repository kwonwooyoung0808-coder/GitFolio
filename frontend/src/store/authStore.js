import { create } from 'zustand'

export const useAuthStore = create((set) => ({
  token: localStorage.getItem('gitfolio_token') || null,
  user: null,
  setToken: (token) => {
    localStorage.setItem('gitfolio_token', token)
    set({ token })
  },
  clearAuth: () => {
    localStorage.removeItem('gitfolio_token')
    set({ token: null, user: null })
  },
}))
