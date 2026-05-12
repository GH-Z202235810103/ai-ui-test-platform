import axios from 'axios'

const API_BASE = '/api/v2'

export async function startRecording(url: string, headless: boolean = false) {
  const { data } = await axios.post(`${API_BASE}/recording/start`, { url, headless })
  return data
}

export async function stopRecording(sessionId: string) {
  const { data } = await axios.post(`${API_BASE}/recording/stop`, { session_id: sessionId })
  return data
}

export async function replayRecording(sessionId: string, url: string, actions: any[], headless: boolean = true) {
  const { data } = await axios.post(`${API_BASE}/recording/replay`, { 
    session_id: sessionId, 
    url, 
    actions, 
    headless 
  })
  return data
}

export async function getRecordings() {
  const { data } = await axios.get(`${API_BASE}/recordings`)
  return data
}

export async function getRecording(id: number) {
  const { data } = await axios.get(`${API_BASE}/recordings/${id}`)
  return data
}

export async function deleteRecording(id: number) {
  const { data } = await axios.delete(`${API_BASE}/recordings/${id}`)
  return data
}
