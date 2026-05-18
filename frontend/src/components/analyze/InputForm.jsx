import { useState } from 'react'
import { useAnalyzeStore } from '../../store/analyzeStore'
import { useSSE } from '../../hooks/useSSE'
import { useAuth } from '../../hooks/useAuth'

export default function InputForm() {
  const [repoUrl, setRepoUrl]   = useState('')
  const [githubId, setGithubId] = useState('')
  const { token } = useAuth()
  const { startStream, status, content, isDone, error } = useSSE()

  const handleSubmit = () => {
    startStream(
      `${import.meta.env.VITE_API_BASE_URL}/analyze/stream`,
      { repo_url: repoUrl, github_id: githubId },
      token
    )
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold text-blue-700">GitFolio 분석</h1>
      <input
        className="w-full border rounded p-3"
        placeholder="GitHub 레포 URL (예: https://github.com/owner/repo)"
        value={repoUrl}
        onChange={e => setRepoUrl(e.target.value)}
      />
      <input
        className="w-full border rounded p-3"
        placeholder="본인 GitHub ID"
        value={githubId}
        onChange={e => setGithubId(e.target.value)}
      />
      <button
        className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700"
        onClick={handleSubmit}
      >
        포트폴리오 생성
      </button>

      {status && <p className="text-sm text-gray-500">⏳ {status}</p>}
      {error  && <p className="text-red-500">❌ {error}</p>}
      {content && (
        <div className="bg-gray-50 border rounded p-4 whitespace-pre-wrap text-sm">
          {content}
        </div>
      )}
      {isDone && (
        <p className="text-green-600 font-bold">✅ 분석 완료! 다운로드 버튼이 활성화됩니다.</p>
      )}
    </div>
  )
}
