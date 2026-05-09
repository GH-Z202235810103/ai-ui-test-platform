<template>
  <div class="project-trends" v-loading="loading">
    <div class="page-header">
      <h2>测试趋势</h2>
      <div class="filters">
        <el-select v-model="projectId" placeholder="选择项目" clearable style="width: 200px; margin-right: 10px;">
          <el-option label="全部项目" :value="null" />
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-select v-model="days" style="width: 120px;">
          <el-option label="近7天" :value="7" />
          <el-option label="近30天" :value="30" />
          <el-option label="近90天" :value="90" />
        </el-select>
      </div>
    </div>

    <template v-if="trendsData">
      <el-row :gutter="20" class="summary-row">
        <el-col :span="8"><SummaryCard :value="trendsData.summary.total_reports" label="总报告数" color="#409EFF" /></el-col>
        <el-col :span="8"><SummaryCard :value="trendsData.summary.avg_pass_rate + '%'" label="平均通过率" color="#67C23A" /></el-col>
        <el-col :span="8"><SummaryCard :value="trendsData.summary.total_tests" label="总测试数" color="#E6A23C" /></el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <LineChart :data="passRateData" title="通过率趋势" color="#67C23A" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <BarChart :data="durationData" title="耗时趋势" color="#409EFF" />
          </el-card>
        </el-col>
      </el-row>

      <el-card class="history-card">
        <template #header><span>历史报告</span></template>
        <el-table :data="trendsData.trends" stripe>
          <el-table-column prop="date" label="日期" />
          <el-table-column prop="total" label="总步骤" />
          <el-table-column prop="passed" label="通过" />
          <el-table-column prop="failed" label="失败" />
          <el-table-column prop="pass_rate" label="通过率">
            <template #default="{ row }">
              <span :style="{ color: row.pass_rate >= 80 ? '#67C23A' : '#F56C6C' }">{{ row.pass_rate }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="avg_duration" label="耗时(s)" />
        </el-table>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getReportTrends } from '../api/report'
import type { TrendsResponse } from '../types/report'
import SummaryCard from '../components/report/SummaryCard.vue'
import LineChart from '../components/charts/LineChart.vue'
import BarChart from '../components/charts/BarChart.vue'

const loading = ref(false)
const projectId = ref<number | null>(null)
const days = ref(30)
const trendsData = ref<TrendsResponse | null>(null)
const projects = ref<{ id: number; name: string }[]>([])

const passRateData = computed(() =>
  trendsData.value?.trends.map(t => ({ date: t.date, value: t.pass_rate })) || []
)

const durationData = computed(() =>
  trendsData.value?.trends.map(t => ({ date: t.date, value: t.avg_duration })) || []
)

async function fetchTrends() {
  loading.value = true
  try {
    trendsData.value = await getReportTrends(projectId.value || undefined, days.value)
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchTrends() })
watch([projectId, days], () => { fetchTrends() })
</script>

<style scoped>
.project-trends { max-width: 1200px; margin: 0 auto; padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
.summary-row { margin-bottom: 20px; }
.history-card { margin-top: 20px; }
</style>
