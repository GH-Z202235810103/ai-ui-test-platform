import axios from 'axios'

const API_BASE = '/api/v2'

export interface Project {
  id: number
  name: string
  description?: string
  base_url?: string
  status?: string
  created_at?: string
}

export async function getProjects() {
  const { data } = await axios.get(`${API_BASE}/projects`)
  return data
}

export async function getProject(id: number) {
  const { data } = await axios.get(`${API_BASE}/projects/${id}`)
  return data
}

export async function createProject(project: Partial<Project>) {
  const { data } = await axios.post(`${API_BASE}/projects`, project)
  return data
}

export async function updateProject(id: number, project: Partial<Project>) {
  const { data } = await axios.put(`${API_BASE}/projects/${id}`, project)
  return data
}

export async function deleteProject(id: number) {
  const { data } = await axios.delete(`${API_BASE}/projects/${id}`)
  return data
}
