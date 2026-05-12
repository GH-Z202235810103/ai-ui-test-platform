<template>
  <div class="project-trends">
    <div class="page-header">
      <h2>测试趋势</h2>
      <div class="filters">
        <el-select 
          v-model="projectId" 
          placeholder="选择项目" 
          clearable 
          style="width: 200px; margin-right: 10px;"
          :loading="projectsLoading"
        >
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

    <el-alert 
      v-if="error" 
      :title="error" 
      type="error" 
      show-icon 
      closable 
      @close="error = ''"
      style="margin-bottom: 20px;"
    />

    <div v-loading="loading" element-loading-text="加载趋势数据中...">
      <template v-if="trendsData">
        <template v-if="trendsData.trends && trendsData.trends.length > 0">
          <el-row :gutter="20" class="summary-row">
            <el-col :span="8">
              <SummaryCard :value="trendsData.summary.total_reports" label="总报告数" color="#409EFF" />
            </el-col>
            <el-col :span="8">
              <SummaryCard :value="trendsData.summary.avg_pass_rate + '%'" label="平均通过率" color="#67C23A" />
            </el-col>
            <el-col :span="8">
              <SummaryCard :value="trendsData.summary.total_tests" label="总测试数" color="#E6A23C" />
            </el-col>
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
                  <span :style="{ color: row.pass_rate >= 80 ? '#67C23A' : '#F56C6C' }">
                    {{ row.pass_rate }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="avg_duration" label="耗时(s)" />
            </el-table>
          </el-card>
        </template>

        <el-empty 
          v-else 
          description="暂无测试报告数据" 
          :image-size="200"
        >
          <template #image>
            <el-icon :size="120" color="#C0C4CC">
              <Document />
            </el-icon>
          </template>
          <el-button type="primary" @click="$router.push('/tasks')">创建测试任务</el-button>
        </el-empty>
      </template>

      <el-empty 
        v-else-if="!loading" 
        description="暂无数据，请先创建测试任务生成报告" 
        :image-size="200"
      >
        <template #image>
          <el-icon :size="120" color="#C0C4CC">
            <TrendCharts />
          </el-icon>
        </template>
        <el-button type="primary" @click="$router.push('/tasks')">创建测试任务</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, TrendCharts } from '@element-plus/icons-vue'
import { getReportTrends } from '../api/report'
import { getProjects } from '../api/project'
import type { TrendsResponse } from '../types/report'
import SummaryCard from '../components/report/SummaryCard.vue'
import LineChart from '../components/charts/LineChart.vue'
import BarChart from '../components/charts/BarChart.vue'

const router = useRouter()
const loading = ref(false)
const projectsLoading = ref(false)
const projectId = ref<number | null>(null)
const days = ref(30)
const trendsData = ref<TrendsResponse | null>(null)
const projects = ref<{ id: number; name: string }[]>([])
const error = ref('')

const passRateData = computed(() =>
  trendsData.value?.trends.map(t => ({ date: t.date, value: t.pass_rate })) || []
)

const durationData = computed(() =>
  trendsData.value?.trends.map(t => ({ date: t.date, value: t.avg_duration })) || []
)

async function fetchProjects() {
  projectsLoading.value = true
  try {
    const res = await getProjects()
    projects.value = res.data || []
  } catch (err) {
    console.error('加载项目列表失败:', err)
  } finally {
    projectsLoading.value = false
  }
}

async function fetchTrends() {
  loading.value = true
  error.value = ''
  try {
    trendsData.value = await getReportTrends(projectId.value || undefined, days.value)
  } catch (err: any) {
    console.error('加载趋势数据失败:', err)
    error.value = err.response?.data?.message || '加载趋势数据失败，请稍后重试'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProjects()
  fetchTrends()
})

watch([projectId, days], () => {
  fetchTrends()
})
</script>

<style scoped>
.project-trends { max-width: 1200px; margin: 0 auto; padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
.summary-row { margin-bottom: 20px; }
.history-card { margin-top: 20px; }
</style>
