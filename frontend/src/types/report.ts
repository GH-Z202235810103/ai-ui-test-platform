export interface ReportStep {
  id: number
  step_index: number
  step_name: string
  step_desc: string
  status: 'passed' | 'failed' | 'skipped'
  duration: number
  error_message: string | null
  expected_screenshot: string | null
  actual_screenshot: string | null
}

export interface TestReport {
  id: number
  task_id: number
  task_name: string
  total_count: number
  pass_count: number
  fail_count: number
  skip_count: number
  pass_rate: number
  duration: number
  status: string
  generated_at: string
  steps: ReportStep[]
}

export interface TrendData {
  date: string
  total: number
  passed: number
  failed: number
  pass_rate: number
  avg_duration: number
}

export interface TrendsResponse {
  project_id: number | null
  date_range: { start: string; end: string }
  trends: TrendData[]
  summary: {
    total_reports: number
    avg_pass_rate: number
    total_tests: number
  }
}
