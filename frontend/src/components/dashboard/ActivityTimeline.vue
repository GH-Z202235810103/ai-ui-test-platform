<template>
  <el-card>
    <template #header>
      <span>最近测试活动</span>
    </template>
    
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    
    <div v-else-if="error" class="error-container">
      <el-icon :size="40"><WarningFilled /></el-icon>
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="activities.length === 0" class="empty-container">
      <el-empty description="暂无测试活动" />
    </div>
    
    <div v-else class="timeline-container">
      <el-timeline>
        <el-timeline-item
          v-for="activity in activities"
          :key="activity.id"
          :timestamp="formatTime(activity.executed_at)"
          placement="top"
        >
          <el-card shadow="hover" class="activity-card" @click="viewDetail(activity.report_id)">
            <div class="activity-content">
              <div class="activity-name">{{ activity.testcase_name }}</div>
              <el-tag :type="getStatusType(activity.status)" size="small">
                {{ getStatusText(activity.status) }}
              </el-tag>
            </div>
            <div class="activity-duration" v-if="activity.duration">
              耗时: {{ activity.duration.toFixed(1) }}s
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import axios from 'axios'

interface Activity {
  id: number
  testcase_name: string
  status: string
  executed_at: string
  duration: number
  report_id: number
}

const activities = ref<Activity[]>([])
const loading = ref(false)
const error = ref('')
const router = useRouter()

const fetchActivities = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const { data } = await axios.get('/api/v2/recent-activities?limit=10')
    if (data.success) {
      activities.value = data.data.activities || []
    }
  } catch (e: any) {
    error.value = e.message || '获取活动数据失败'
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return ''
  
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

onMounted(() => {
  fetchActivities()
})
</script>

<style scoped>
.timeline-container {
  max-height: 400px;
  overflow-y: auto;
}

.activity-card {
  cursor: pointer;
  margin-bottom: 10px;
}

.activity-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.activity-name {
  font-weight: 500;
  color: #303133;
}

.activity-duration {
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
