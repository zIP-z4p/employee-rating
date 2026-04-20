import axios, { AxiosInstance } from 'axios'

// Vite использует import.meta.env вместо process.env
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

export interface RatingSnapshot {
  employee_id: string
  employee_name: string
  department_name: string
  period: string
  total_score: number
  rank: number
  department_rank: number
  percentile: number
  delta_score: number | null
  delta_rank: number | null
}

export interface TrendPoint {
  period: string
  total_score: number
  rank: number
  percentile: number
  delta_score: number | null
}

export const ratingsApi = {
  getSnapshot: (period: string, topN?: number) =>
    apiClient.get<RatingSnapshot[]>(`/ratings/snapshots/${period}`, {
      params: topN ? { top_n: topN } : undefined,
    }),

  getEmployeeTrend: (employeeId: string, months = 6) =>
    apiClient.get(`/ratings/analytics/trends`, {
      params: { employee_id: employeeId, months },
    }),

  buildSnapshot: (period: string) =>
    apiClient.post(`/ratings/snapshots/build`, null, {
      params: { period },
    }),

  importCSV: (file: File, period: string) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/ratings/import', formData, {
      params: { period },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

