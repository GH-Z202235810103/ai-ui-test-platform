<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409EFF;">
              <el-icon size="32"><Folder /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.projects }}</div>
              <div class="stat-label">项目总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67C23A;">
              <el-icon size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.testcases }}</div>
              <div class="stat-label">测试用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #E6A23C;">
              <el-icon size="32"><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.tasks }}</div>
              <div class="stat-label">测试任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #F56C6C;">
              <el-icon size="32"><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.reports }}</div>
              <div class="stat-label">测试报告</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/projects')">管理项目</el-button>
            <el-button type="success" @click="$router.push('/testcases')">创建用例</el-button>
            <el-button type="warning" @click="$router.push('/tasks')">新建任务</el-button>
            <el-button type="info" @click="$router.push('/recording')">录制回放</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 测试执行趋势图 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <TrendChart />
      </el-col>
    </el-row>

    <!-- 测试状态分布 + 最近执行记录 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <StatusPieChart />
      </el-col>
      <el-col :span="12">
        <RecentExecutions />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Folder, Document, List, DataAnalysis } from '@element-plus/icons-vue'
import api from '../api/index'
import TrendChart from '../components/dashboard/TrendChart.vue'
import StatusPieChart from '../components/dashboard/StatusPieChart.vue'
import RecentExecutions from '../components/dashboard/RecentExecutions.vue'

const stats = ref({
  projects: 0,
  testcases: 0,
  tasks: 0,
  reports: 0,
  task_status: {
    pending: 0,
    running: 0,
    success: 0,
    failed: 0
  }
})

async function fetchStats() {
  try {
    const { data } = await api.get('/v2/statistics')
    if (data.success) {
      stats.value = data.data
    }
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.stat-card {
  cursor: pointer;
}
.stat-content {
  display: flex;
  align-items: center;
}
.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 16px;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
