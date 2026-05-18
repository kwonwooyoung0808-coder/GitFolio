import { create } from 'zustand'

export const useAnalyzeStore = create((set) => ({
  repoUrl:   '',
  githubId:  '',
  status:    '',
  content:   '',
  isDone:    false,
  error:     null,
  setInput:  (repoUrl, githubId) => set({ repoUrl, githubId }),
  setStatus: (status)  => set({ status }),
  appendContent: (chunk) => set((s) => ({ content: s.content + chunk })),
  setDone:   () => set({ isDone: true }),
  setError:  (error) => set({ error }),
  reset:     () => set({ status: '', content: '', isDone: false, error: null }),
}))
