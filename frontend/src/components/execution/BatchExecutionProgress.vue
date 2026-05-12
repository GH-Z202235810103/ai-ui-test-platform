<template>
  <el-dialog
    v-model="visible"
    title="批量执行进度"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="batch-execution-progress">
      <div class="batch-header">
        <div class="batch-stats">
          <div class="stat-item">
            <span class="stat-label">总计:</span>
            <span class="stat-value">{{ executionList.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">执行中:</span>
            <span class="stat-value running">{{ runningCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">成功:</span>
            <span class="stat-value success">{{ successCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">失败:</span>
            <span class="stat-value failed">{{ failedCount }}</span>
          </div>
        </div>
        <el-progress 
          :percentage="overallProgress" 
          :status="overallStatus"
          :stroke-width="15"
        />
      </div>

      <div class="execution-list">
        <el-table :data="executionList" max-height="400" stripe>
          <el-table-column prop="testcase_name" label="用例名称" min-width="150" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="150">
            <template #default="{ row }">
              <el-progress 
                :percentage="row.progress || 0" 
                :show-text="false"
                :status="getProgressStatus(row.status)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button 
                size="small" 
                type="primary"
                link
                @click="handleViewDetail(row)"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button 
          v-if="isAllCompleted"
          type="primary"
          @click="handleViewReports"
        >
          查看报告
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getExecutionStatus, type ExecutionResult } from '../../api/testcase'

interface ExecutionItem {
  test_case_id: number
  execution_id: string
  testcase_name: string
  status: string
  progress: number
}

interface Props {
  modelValue: boolean
  executionIds: Array<{
    test_case_id: number
    execution_id: string
    testcase_name: string
    status: string
  }>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'view-detail': [execution: ExecutionItem]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const executionList = ref<ExecutionItem[]>([])
const pollTimer = ref<number | null>(null)

const runningCount = computed(() => {
  return executionList.value.filter(item => 
    item.status === 'running' || item.status === 'pending'
  ).length
})

const successCount = computed(() => {
  return executionList.value.filter(item => 
    item.status === 'passed' || item.status === 'success'
  ).length
})

const failedCount = computed(() => {
  return executionList.value.filter(item => item.status === 'failed').length
})

const overallProgress = computed(() => {
  if (executionList.value.length === 0) return 0
  const totalProgress = executionList.value.reduce((sum, item) => sum + (item.progress || 0), 0)
  return Math.round(totalProgress / executionList.value.length)
})

const overallStatus = computed(() => {
  if (runningCount.value > 0) return undefined
  if (failedCount.value > 0) return 'exception'
  return 'success'
})

const isAllCompleted = computed(() => {
  return runningCount.value === 0 && executionList.value.length > 0
})

async function fetchExecutionStatuses() {
  const updates = await Promise.all(
    executionList.value.map(async (item) => {
      if (item.status === 'running' || item.status === 'pending') {
        try {
          const result = await getExecutionStatus(item.execution_id)
          return {
            ...item,
            status: result.status,
            progress: result.progress
          }
        } catch (error) {
          console.error(`获取执行状态失败: ${item.execution_id}`, error)
          return item
        }
      }
      return item
    })
  )

  executionList.value = updates

  if (runningCount.value === 0) {
    stopPolling()
    ElMessage.success('批量执行已完成')
  }
}

function startPolling() {
  stopPolling()
  pollTimer.value = window.setInterval(() => {
    fetchExecutionStatuses()
  }, 3000)
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

function handleClose() {
  stopPolling()
  visible.value = false
}

function handleViewDetail(execution: ExecutionItem) {
  emit('view-detail', execution)
}

function handleViewReports() {
  ElMessage.info('批量报告查看功能开发中')
}

function getStatusType(status: string) {
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
}

function getStatusText(status: string) {
  switch (status) {
    case 'pending':
      return '等待中'
    case 'running':
      return '执行中'
    case 'passed':
    case 'success':
      return '成功'
    case 'failed':
      return '失败'
    default:
      return '未知'
  }
}

function getProgressStatus(status: string) {
  if (status === 'passed' || status === 'success') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
}

watch(() => props.executionIds, (newIds) => {
  if (newIds && newIds.length > 0) {
    executionList.value = newIds.map(item => ({
      ...item,
      progress: 0
    }))
    startPolling()
  }
}, { immediate: true })

watch(visible, (newVal) => {
  if (!newVal) {
    stopPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.batch-execution-progress {
  min-height: 400px;
}

.batch-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.batch-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.stat-value.running {
  color: #e6a23c;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.failed {
  color: #f56c6c;
}

.execution-list {
  margin-top: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
