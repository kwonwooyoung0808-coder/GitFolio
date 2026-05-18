import { useCallback, useState } from 'react'

export function useAnalyzeStream() {
  const [repoUrl, setRepoUrl] = useState('')
  const [githubIdentity, setGithubIdentity] = useState('')
  const [status, setStatus] = useState('')
  const [content, setContent] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [isDone, setIsDone] = useState(false)

  const startStream = useCallback(async (url, body, token) => {
    setStatus('분석을 시작했습니다.')
    setContent('')
    setResult(null)
    setError(null)
    setIsDone(false)

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    })

    if (!response.ok || !response.body) {
      throw new Error('스트리밍 요청에 실패했습니다.')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const chunks = buffer.split('\n\n')
      buffer = chunks.pop() || ''

      for (const chunk of chunks) {
        const line = chunk.split('\n').find((item) => item.startsWith('data: '))
        if (!line) continue

        try {
          const { type, data } = JSON.parse(line.slice(6))
          if (type === 'status') setStatus(data)
          if (type === 'chunk') setContent((prev) => prev + data)
          if (type === 'done') {
            setResult(data)
            setIsDone(true)
          }
          if (type === 'error') setError(data)
        } catch (_) {
          // ignore malformed chunks
        }
      }
    }
  }, [])

  return {
    repoUrl,
    githubIdentity,
    setRepoUrl,
    setGithubIdentity,
    status,
    content,
    result,
    error,
    isDone,
    startStream,
  }
}
