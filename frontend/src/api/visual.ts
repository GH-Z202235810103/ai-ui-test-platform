import axios from 'axios'

const API_BASE = '/api/v2'

export async function getVisualTemplates() {
  const { data } = await axios.get(`${API_BASE}/visual/templates`)
  return data
}

export async function createVisualTemplate(formData: FormData) {
  const { data } = await axios.post(`${API_BASE}/visual/templates`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export async function deleteVisualTemplate(name: string) {
  const { data } = await axios.delete(`${API_BASE}/visual/templates/${name}`)
  return data
}

export async function locateElement(screenshot: File, elementName: string) {
  const formData = new FormData()
  formData.append('screenshot', screenshot)
  formData.append('element_name', elementName)
  const { data } = await axios.post(`${API_BASE}/visual/locate`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}
