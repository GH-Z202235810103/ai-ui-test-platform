<template>
  <div class="report-detail" v-loading="loading">
    <div class="page-header">
      <el-page-header @back="goBack" :content="'测试报告 #' + id" />
      <ExportButton v-if="report" :report-id="Number(id)" />
    </div>

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
            <PieChart :passed="report.pass_count" :failed="report.fail_count" :skipped="report.skip_count" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <div class="info-list">
              <div class="info-item"><span class="label">通过率</span><span class="value" :style="{ color: report.pass_rate >= 80 ? '#67C23A' : '#F56C6C' }">{{ report.pass_rate }}%</span></div>
              <div class="info-item"><span class="label">总耗时</span><span class="value">{{ report.duration }}秒</span></div>
              <div class="info-item"><span class="label">状态</span><span class="value">{{ report.status }}</span></div>
              <div class="info-item"><span class="label">生成时间</span><span class="value">{{ report.generated_at }}</span></div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="steps-card">
        <template #header><span>步骤详情</span></template>
        <StepTable :steps="report.steps" />
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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

onMounted(async () => {
  loading.value = true
  try {
    report.value = await getReportDetail(Number(id))
  } catch (error) {
    console.error('加载报告失败:', error)
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.push('/reports/trends')
}
</script>

<style scoped>
.report-detail { max-width: 1200px; margin: 0 auto; padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.summary-row { margin-bottom: 20px; }
.info-list { padding: 10px; }
.info-item { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #ebeef5; }
.info-item .label { color: #909399; }
.info-item .value { font-weight: bold; }
.steps-card { margin-top: 20px; }
</style>
