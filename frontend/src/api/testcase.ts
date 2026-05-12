import axios from 'axios'

const API_BASE = '/api/v2'

export interface TestCase {
  id: number
  name: string
  description?: string
  script_data: any
  type?: string
  project_id?: number
  status?: string
  version?: number
}

export async function getTestCases(projectId?: number) {
  const params: any = {}
  if (projectId) params.project_id = projectId
  const { data } = await axios.get(`${API_BASE}/testcases`, { params })
  return data
}

export async function getTestCase(id: number) {
  const { data } = await axios.get(`${API_BASE}/testcases/${id}`)
  return data
}

export async function createTestCase(testCase: Partial<TestCase>) {
  const { data } = await axios.post(`${API_BASE}/testcases`, testCase)
  return data
}

export async function updateTestCase(id: number, testCase: Partial<TestCase>) {
  const { data } = await axios.put(`${API_BASE}/testcases/${id}`, testCase)
  return data
}

export async function deleteTestCase(id: number) {
  const { data } = await axios.delete(`${API_BASE}/testcases/${id}`)
  return data
}

export interface ExecutionConfig {
  headless?: boolean
  timeout?: number
  retryCount?: number
  screenshotQuality?: number
  screenshotEnabled?: boolean
}

export async function executeTestCase(id: number, config?: ExecutionConfig) {
  const params = {
    test_case_id: id,
    headless: config?.headless ?? true,
    timeout: config?.timeout ?? 30,
    retry_count: config?.retryCount ?? 3,
    screenshot_quality: config?.screenshotQuality ?? 80,
    screenshot_enabled: config?.screenshotEnabled ?? true
  }
  const { data } = await axios.post(`${API_BASE}/execute`, params)
  return data
}

export async function generateFromNlp(description: string) {
  const { data } = await axios.post(`${API_BASE}/generate-from-nlp`, { description })
  return data
}

export interface ExecutionResult {
  success: boolean
  execution_id: string
  testcase_id: number
  testcase_name: string
  status: string
  start_time?: string
  end_time?: string
  duration?: string
  execution_log?: string[]
  screenshots?: string[]
  error?: string
  progress?: number
  report_id?: number
}

export interface BatchExecutionResult {
  success: boolean
  batch_id: string
  total: number
  execution_ids: Array<{
    test_case_id: number
    execution_id: string
    testcase_name: string
    status: string
  }>
  message: string
}

export async function getExecutionResult(executionId: string): Promise<ExecutionResult> {
  const { data } = await axios.get(`${API_BASE}/execution/${executionId}`)
  return data
}

export async function getExecutionStatus(executionId: string) {
  const { data } = await axios.get(`${API_BASE}/execution/${executionId}/status`)
  return data
}

export async function getExecutionLogs(executionId: string) {
  const { data } = await axios.get(`${API_BASE}/execution/${executionId}/logs`)
  return data
}

export async function executeBatch(testCaseIds: number[], config?: ExecutionConfig): Promise<BatchExecutionResult> {
  const params = { 
    test_case_ids: testCaseIds, 
    headless: config?.headless ?? true,
    timeout: config?.timeout ?? 30,
    retry_count: config?.retryCount ?? 3,
    screenshot_quality: config?.screenshotQuality ?? 80,
    screenshot_enabled: config?.screenshotEnabled ?? true
  }
  const { data } = await axios.post(`${API_BASE}/execute/batch`, params)
  return data
}
