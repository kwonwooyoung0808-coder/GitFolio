import { useState, useRef, useCallback } from 'react'

/**
 * SSE 스트리밍 커스텀 훅
 * 분석 진행 상황과 LLM 청크를 실시간 수신
 */
export function useSSE() {
  const [status, setStatus]   = useState('')
  const [content, setContent] = useState('')
  const [isDone, setIsDone]   = useState(false)
  const [error, setError]     = useState(null)
  const esRef = useRef(null)

  const startStream = useCallback(async (url, body, token) => {
    setStatus('분석 시작...')
    setContent('')
    setIsDone(false)
    setError(null)

    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    })

    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const lines = decoder.decode(value).split('\n')
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const { type, data } = JSON.parse(line.slice(6))
          if (type === 'status') setStatus(data)
          if (type === 'chunk')  setContent(prev => prev + data)
          if (type === 'done')   setIsDone(true)
          if (type === 'error')  setError(data)
        } catch (_) {}
      }
    }
  }, [])

  return { status, content, isDone, error, startStream }
}
