import axios from 'axios'

const API_BASE = '/api/v2'

export interface TestTask {
  id: number
  name: string
  type?: string
  execution_status?: string
  project_id?: number
  case_ids?: number[]
  progress?: number
  started_at?: string
  finished_at?: string
}

export async function getTasks(projectId?: number) {
  const params: any = {}
  if (projectId) params.project_id = projectId
  const { data } = await axios.get(`${API_BASE}/tasks`, { params })
  return data
}

export async function getTask(id: number) {
  const { data } = await axios.get(`${API_BASE}/tasks/${id}`)
  return data
}

export async function createTask(task: Partial<TestTask>) {
  const { data } = await axios.post(`${API_BASE}/tasks`, task)
  return data
}

export async function updateTaskStatus(id: number, status: string, progress?: number) {
  const params: any = { status }
  if (progress !== undefined) params.progress = progress
  const { data } = await axios.put(`${API_BASE}/tasks/${id}/status`, null, { params })
  return data
}

export async function deleteTask(id: number) {
  const { data } = await axios.delete(`${API_BASE}/tasks/${id}`)
  return data
}
