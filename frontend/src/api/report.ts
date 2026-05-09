import axios from 'axios'
import type { TestReport, TrendsResponse } from '../types/report'

const API_BASE = '/api/v2'

export async function getReportDetail(reportId: number): Promise<TestReport> {
  const { data } = await axios.get(`${API_BASE}/reports/${reportId}`)
  return data.data
}

export async function getReportTrends(projectId?: number, days: number = 30): Promise<TrendsResponse> {
  const params: Record<string, any> = { days }
  if (projectId) params.project_id = projectId
  const { data } = await axios.get(`${API_BASE}/reports/trends/overview`, { params })
  return data.data
}

export async function exportReport(reportId: number, format: 'pdf' | 'html'): Promise<Blob> {
  const { data } = await axios.get(`${API_BASE}/reports/${reportId}/export`, {
    params: { format },
    responseType: 'blob'
  })
  return data
}

export async function getReportsList(taskId?: number) {
  const params: Record<string, any> = {}
  if (taskId) params.task_id = taskId
  const { data } = await axios.get(`${API_BASE}/reports`, { params })
  return data
}
