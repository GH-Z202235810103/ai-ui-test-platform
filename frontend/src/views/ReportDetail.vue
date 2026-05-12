<template>
  <div class="report-detail" v-loading="loading">
    <div class="page-header">
      <el-page-header @back="goBack" :content="'测试报告 #' + id" />
      <ExportButton v-if="report" :report-id="Number(id)" />
    </div>

    <el-empty v-if="!loading && !report && !error" description="报告不存在或已被删除">
      <el-button type="primary" @click="goBack">返回列表</el-button>
    </el-empty>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="error-alert"
    >
      <template #default>
        <p>请检查报告ID是否正确，或联系管理员</p>
        <el-button type="primary" size="small" @click="loadReport" style="margin-top: 10px;">重新加载</el-button>
      </template>
    </el-alert>

    <template v-if="report">
      <el-row :gutter="20" class="summary-row">
        <el-col :span="6"><SummaryCard :value="report.total_count" label="总步骤数" color="#409EFF" /></el-col>
        <el-col :span="6"><SummaryCard :value="report.pass_count" label="通过" color="#67C23A" /></el-col>
        <el-col :span="6"><SummaryCard :value="report.fail_count" label="失败" color="#F56C6C" /></el-col>
        <el-col :span="6"><SummaryCard :value="report.skip_count" label="跳过" color="#E6A23C" /></el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>执行结果分布</span>
                <el-tag v-if="report.pass_rate >= 80" type="success">优秀</el-tag>
                <el-tag v-else-if="report.pass_rate >= 60" type="warning">良好</el-tag>
                <el-tag v-else type="danger">需改进</el-tag>
              </div>
            </template>
            <PieChart :passed="report.pass_count" :failed="report.fail_count" :skipped="report.skip_count" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>报告信息</template>
            <div class="info-list">
              <div class="info-item">
                <span class="label">所属任务</span>
                <span class="value">{{ report.task_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">通过率</span>
                <span class="value" :style="{ color: report.pass_rate >= 80 ? '#67C23A' : '#F56C6C' }">
                  {{ report.pass_rate.toFixed(1) }}%
                </span>
              </div>
              <div class="info-item">
                <span class="label">总耗时</span>
                <span class="value">{{ formatDuration(report.duration) }}</span>
              </div>
              <div class="info-item">
                <span class="label">状态</span>
                <el-tag :type="report.status === 'completed' ? 'success' : 'info'" size="small">
                  {{ report.status === 'completed' ? '已完成' : report.status }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">生成时间</span>
                <span class="value">{{ formatDateTime(report.generated_at) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="steps-card">
        <template #header>
          <div class="card-header">
            <span>步骤详情</span>
            <el-tag type="info" size="small">共 {{ report.steps?.length || 0 }} 个步骤</el-tag>
          </div>
        </template>
        <StepTable :steps="report.steps" />
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getReportDetail } from '../api/report'
import type { TestReport } from '../types/report'
import SummaryCard from '../components/report/SummaryCard.vue'
import StepTable from '../components/report/StepTable.vue'
import PieChart from '../components/charts/PieChart.vue'
import ExportButton from '../components/report/ExportButton.vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string

const loading = ref(false)
const report = ref<TestReport | null>(null)
const error = ref<string | null>(null)

onMounted(() => {
  loadReport()
})

async function loadReport() {
  if (!id || isNaN(Number(id))) {
    error.value = '无效的报告ID'
    return
  }

  loading.value = true
  error.value = null

  try {
    report.value = await getReportDetail(Number(id))
    if (!report.value) {
      error.value = '报告不存在'
    }
  } catch (err: any) {
    console.error('加载报告失败:', err)
    error.value = err.response?.data?.message || '加载报告失败，请稍后重试'
    ElMessage.error(error.value || '加载报告失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/reports/trends')
}

function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}秒`
  }
  const minutes = Math.floor(seconds / 60)
  const secs = (seconds % 60).toFixed(0)
  return `${minutes}分${secs}秒`
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.report-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-row {
  margin-bottom: 20px;
}

.error-alert {
  margin-bottom: 20px;
}

.info-list {
  padding: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #909399;
  font-size: 14px;
}

.info-item .value {
  font-weight: 600;
  font-size: 14px;
}

.steps-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .report-detail {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .summary-row .el-col {
    margin-bottom: 10px;
  }
}
</style>
