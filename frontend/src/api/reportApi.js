import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

function authHeaders(token) {
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
}

function toReadableError(error) {
  const status = error?.response?.status

  if (status === 401) {
    return new Error('로그인이 필요하거나 세션이 만료되었습니다. 다시 로그인해주세요.')
  }

  if (status === 403) {
    return new Error('이 보고서에 접근할 권한이 없습니다.')
  }

  if (status === 404) {
    return new Error('요청한 데이터를 찾을 수 없습니다.')
  }

  return new Error(error?.response?.data?.detail || error?.message || '요청 처리 중 오류가 발생했습니다.')
}

export async function fetchReports(token) {
  try {
    const response = await api.get('/reports', authHeaders(token))
    return response.data.reports
  } catch (error) {
    throw toReadableError(error)
  }
}

export async function fetchReport(reportId, token) {
  try {
    const response = await api.get(`/reports/${reportId}`, authHeaders(token))
    return response.data
  } catch (error) {
    throw toReadableError(error)
  }
}

export async function updateReportMeta(reportId, payload, token) {
  try {
    const response = await api.patch(`/reports/${reportId}`, payload, authHeaders(token))
    return response.data
  } catch (error) {
    throw toReadableError(error)
  }
}
