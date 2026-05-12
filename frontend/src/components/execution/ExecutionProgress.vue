<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="800px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="handleClose"
  >
    <div class="execution-progress">
      <div class="progress-header">
        <div class="status-info">
          <el-tag :type="statusType" size="large">
            {{ statusText }}
          </el-tag>
          <span class="testcase-name">{{ executionResult?.testcase_name || '加载中...' }}</span>
        </div>
        <div class="time-info" v-if="executionResult">
          <div class="timer-display" v-if="isRunning">
            <el-icon class="timer-icon"><Timer /></el-icon>
            <span class="timer-text">{{ formattedTimer }}</span>
          </div>
          <div v-if="executionResult.start_time">
            开始时间: {{ formatDate(executionResult.start_time) }}
          </div>
          <div v-if="executionResult.end_time">
            结束时间: {{ formatDate(executionResult.end_time) }}
          </div>
          <div v-if="executionResult.duration">
            执行时长: {{ executionResult.duration }}秒
          </div>
        </div>
      </div>

      <div class="progress-bar-container">
        <el-progress 
          :percentage="progress" 
          :status="progressStatus"
          :stroke-width="20"
        />
        <div class="progress-text">{{ progressText }}</div>
      </div>

      <div class="execution-info" v-if="executionResult">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="执行日志" name="logs">
            <div class="logs-container">
              <div 
                v-for="(log, index) in executionResult.execution_log" 
                :key="index"
                class="log-item"
                :class="getLogClass(log)"
              >
                <span class="log-time">{{ formatLogTime(index) }}</span>
                <span class="log-content">{{ log }}</span>
              </div>
              <div v-if="!executionResult.execution_log?.length" class="no-logs">
                暂无执行日志
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="截图" name="screenshots">
            <div class="screenshots-container">
              <div 
                v-for="(screenshot, index) in executionResult.screenshots" 
                :key="index"
                class="screenshot-item"
              >
                <el-image 
                  :src="getScreenshotUrl(screenshot)"
                  :preview-src-list="[getScreenshotUrl(screenshot)]"
                  fit="contain"
                  class="screenshot-image"
                />
                <div class="screenshot-name">{{ getScreenshotName(screenshot) }}</div>
              </div>
              <div v-if="!executionResult.screenshots?.length" class="no-screenshots">
                暂无截图
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="错误信息" name="error" v-if="executionResult.error">
            <div class="error-container">
              <el-alert
                title="执行错误"
                type="error"
                :closable="false"
              >
                <pre>{{ executionResult.error }}</pre>
              </el-alert>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button 
          v-if="executionResult?.status === 'running'" 
          type="danger"
          @click="handleStop"
        >
          停止执行
        </el-button>
        <el-button 
          v-if="isCompleted && executionResult?.report_id"
          type="success"
          @click="handleViewReport"
        >
          <el-icon><Document /></el-icon>
          查看测试报告
        </el-button>
        <el-dropdown 
          v-if="isCompleted && executionResult?.report_id"
          @command="handleExport"
        >
          <el-button type="primary">
            导出报告 <el-icon class="el-icon--right"><Download /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="html">导出为 HTML</el-dropdown-item>
              <el-dropdown-item command="pdf">导出为 PDF</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Timer, Download, Document } from '@element-plus/icons-vue'
import { getExecutionResult, type ExecutionResult } from '../../api/testcase'
import { useRouter } from 'vue-router'

interface Props {
  modelValue: boolean
  executionId: string | null
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '执行进度'
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'completed': [result: ExecutionResult]
  'stop': []
}>()

const router = useRouter()

function handleViewReport() {
  if (executionResult.value?.report_id) {
    router.push({ name: 'ReportDetail', params: { id: executionResult.value.report_id } })
    visible.value = false
  }
}

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const executionResult = ref<ExecutionResult | null>(null)
const activeTab = ref('logs')
const pollTimer = ref<number | null>(null)
const executionTimer = ref<number | null>(null)
const timerSeconds = ref(0)
const startTime = ref<Date | null>(null)

const statusType = computed(() => {
  const status = executionResult.value?.status
  switch (status) {
    case 'passed':
    case 'success':
      return 'success'
    case 'failed':
      return 'danger'
    case 'running':
      return 'warning'
    default:
      return 'info'
  }
})

const statusText = computed(() => {
  const status = executionResult.value?.status
  switch (status) {
    case 'pending':
      return '等待中'
    case 'running':
      return '执行中'
    case 'passed':
    case 'success':
      return '执行成功'
    case 'failed':
      return '执行失败'
    default:
      return '未知状态'
  }
})

const progress = computed(() => {
  return executionResult.value?.progress || 0
})

const progressStatus = computed(() => {
  const status = executionResult.value?.status
  if (status === 'passed' || status === 'success') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
})

const progressText = computed(() => {
  const status = executionResult.value?.status
  if (status === 'pending') return '准备执行...'
  if (status === 'running') return '正在执行测试用例...'
  if (status === 'passed' || status === 'success') return '执行完成 - 通过'
  if (status === 'failed') return '执行完成 - 失败'
  return '准备中...'
})

const isCompleted = computed(() => {
  const status = executionResult.value?.status
  return status === 'passed' || status === 'success' || status === 'failed'
})

const isRunning = computed(() => {
  const status = executionResult.value?.status
  return status === 'running' || status === 'pending'
})

const formattedTimer = computed(() => {
  const hours = Math.floor(timerSeconds.value / 3600)
  const minutes = Math.floor((timerSeconds.value % 3600) / 60)
  const seconds = timerSeconds.value % 60
  
  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

async function fetchExecutionResult() {
  if (!props.executionId) return

  try {
    const result = await getExecutionResult(props.executionId)
    executionResult.value = result

    if (result.status === 'running' || result.status === 'pending') {
      startPolling()
      if (!executionTimer.value) {
        startTimer()
      }
    } else {
      stopPolling()
      stopTimer()
      if (isCompleted.value) {
        emit('completed', result)
      }
    }
  } catch (error) {
    console.error('获取执行结果失败:', error)
    ElMessage.error('获取执行结果失败')
    stopPolling()
    stopTimer()
  }
}

function startPolling() {
  stopPolling()
  pollTimer.value = window.setInterval(() => {
    fetchExecutionResult()
  }, 2000)
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

function startTimer() {
  stopTimer()
  startTime.value = new Date()
  timerSeconds.value = 0
  executionTimer.value = window.setInterval(() => {
    timerSeconds.value++
  }, 1000)
}

function stopTimer() {
  if (executionTimer.value) {
    clearInterval(executionTimer.value)
    executionTimer.value = null
  }
}

function handleClose() {
  stopPolling()
  stopTimer()
  visible.value = false
  executionResult.value = null
  activeTab.value = 'logs'
  timerSeconds.value = 0
  startTime.value = null
}

function handleStop() {
  emit('stop')
  stopPolling()
}

function handleExport(format: string) {
  if (!executionResult.value?.report_id) {
    ElMessage.warning('报告ID不存在，无法导出')
    return
  }
  
  const reportId = executionResult.value.report_id
  const url = `/api/v2/reports/${reportId}/export?format=${format}`
  
  const link = document.createElement('a')
  link.href = url
  link.download = `report_${reportId}.${format}`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success(`正在导出${format.toUpperCase()}格式报告...`)
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function formatLogTime(index: number) {
  const now = new Date()
  now.setSeconds(now.getSeconds() - (executionResult.value?.execution_log?.length || 0) + index)
  return now.toLocaleTimeString('zh-CN')
}

function getLogClass(log: string) {
  if (log.includes('错误') || log.includes('失败') || log.includes('error')) {
    return 'log-error'
  }
  if (log.includes('成功') || log.includes('完成') || log.includes('success')) {
    return 'log-success'
  }
  return ''
}

function getScreenshotUrl(screenshot: string) {
  if (screenshot.startsWith('http')) return screenshot
  return `/api/v2/screenshots/${screenshot}`
}

function getScreenshotName(screenshot: string) {
  return screenshot.split('/').pop() || screenshot
}

watch(() => props.executionId, (newId) => {
  if (newId && visible.value) {
    fetchExecutionResult()
  }
})

watch(visible, (newVal) => {
  if (newVal && props.executionId) {
    fetchExecutionResult()
  } else {
    stopPolling()
    stopTimer()
  }
})

onUnmounted(() => {
  stopPolling()
  stopTimer()
})
</script>

<style scoped>
.execution-progress {
  min-height: 400px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.testcase-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.time-info {
  text-align: right;
  color: #606266;
  font-size: 14px;
  line-height: 1.8;
}

.timer-display {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: #fff;
  font-weight: 500;
}

.timer-icon {
  font-size: 18px;
  animation: pulse 1s ease-in-out infinite;
}

.timer-text {
  font-size: 18px;
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.progress-bar-container {
  margin-bottom: 24px;
}

.progress-text {
  text-align: center;
  margin-top: 8px;
  color: #606266;
  font-size: 14px;
}

.execution-info {
  min-height: 300px;
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.log-item {
  padding: 8px 12px;
  margin-bottom: 8px;
  background-color: #fff;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.log-item.log-error {
  border-left-color: #f56c6c;
  background-color: #fef0f0;
}

.log-item.log-success {
  border-left-color: #67c23a;
  background-color: #f0f9ff;
}

.log-time {
  color: #909399;
  font-size: 12px;
  margin-right: 12px;
}

.log-content {
  color: #303133;
  font-size: 14px;
}

.no-logs,
.no-screenshots {
  text-align: center;
  color: #909399;
  padding: 40px;
}

.screenshots-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  padding: 12px;
}

.screenshot-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.screenshot-image {
  width: 100%;
  height: 150px;
  cursor: pointer;
}

.screenshot-name {
  padding: 8px;
  text-align: center;
  font-size: 12px;
  color: #606266;
  background-color: #f5f7fa;
}

.error-container {
  padding: 12px;
}

.error-container pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
