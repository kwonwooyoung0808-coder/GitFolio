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

export async function fetchReports(token) {
  const response = await api.get('/reports', authHeaders(token))
  return response.data.reports
}

export async function fetchReport(reportId, token) {
  const response = await api.get(`/reports/${reportId}`, authHeaders(token))
  return response.data
}
