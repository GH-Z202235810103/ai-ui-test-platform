<template>
  <el-card>
    <template #header>
      <div class="header-container">
        <span>最近执行记录</span>
        <el-button text type="primary" @click="viewAll">
          查看全部
        </el-button>
      </div>
    </template>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>

    <div v-else-if="error" class="error-container">
      <el-icon :size="40"><WarningFilled /></el-icon>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="executions.length === 0" class="empty-container">
      <el-empty description="暂无执行记录" />
    </div>

    <el-table v-else :data="executions" style="width: 100%" max-height="300">
      <el-table-column prop="testcase_name" label="用例名称" min-width="150">
        <template #default="{ row }">
          <span class="testcase-name">{{ row.testcase_name }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="executed_at" label="执行时间" width="140">
        <template #default="{ row }">
          <span class="time-text">{{ formatTime(row.executed_at) }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="duration" label="耗时" width="80">
        <template #default="{ row }">
          <span v-if="row.duration">{{ row.duration.toFixed(1) }}s</span>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="viewDetail(row.report_id)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import axios from 'axios'

interface Execution {
  id: number
  testcase_name: string
  status: string
  executed_at: string
  duration: number
  report_id: number
}

const executions = ref<Execution[]>([])
const loading = ref(true)
const error = ref('')
const router = useRouter()

const fetchExecutions = async () => {
  loading.value = true
  error.value = ''

  try {
    const { data } = await axios.get('/api/v2/recent-activities?limit=10')
    if (data.success) {
      executions.value = data.data.activities || []
    }
  } catch (e: any) {
    error.value = e.message || '获取执行记录失败'
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return '-'

  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    passed: 'success',
    failed: 'danger',
    running: 'warning',
    pending: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    passed: '成功',
    failed: '失败',
    running: '运行中',
    pending: '待执行'
  }
  return texts[status] || status
}

const viewDetail = (reportId: number) => {
  router.push(`/reports/${reportId}`)
}

const viewAll = () => {
  router.push('/reports')
}

onMounted(() => {
  fetchExecutions()
})
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.testcase-name {
  font-weight: 500;
  color: #303133;
}

.time-text {
  font-size: 12px;
  color: #909399;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #909399;
}

.error-container {
  color: #F56C6C;
}
</style>