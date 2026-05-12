<template>
  <el-card>
    <template #header>
      <span>整体通过率</span>
    </template>
    
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    
    <div v-else-if="error" class="error-container">
      <el-icon :size="40"><WarningFilled /></el-icon>
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="!passRateData" class="empty-container">
      <el-empty description="暂无数据" />
    </div>
    
    <div v-else>
      <div ref="chartRef" class="chart-container"></div>
      <div class="legend">
        <div class="legend-item">
          <span class="legend-color" style="background: #67C23A;"></span>
          <span>通过: {{ passRateData.passed }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #F56C6C;"></span>
          <span>失败: {{ passRateData.failed }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #909399;"></span>
          <span>跳过: {{ passRateData.skipped }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import axios from 'axios'

interface PassRateStats {
  total: number
  passed: number
  failed: number
  skipped: number
  pass_rate: number
}

const passRateData = ref<PassRateStats | null>(null)
const loading = ref(false)
const error = ref('')
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const fetchPassRate = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const { data } = await axios.get('/api/v2/statistics')
    if (data.success) {
      passRateData.value = data.data.pass_rate_stats
      await nextTick()
      renderChart()
    }
  } catch (e: any) {
    error.value = e.message || '获取通过率数据失败'
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  if (!chartRef.value || !passRateData.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '测试结果',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'center',
          formatter: () => {
            return `{a|${passRateData.value!.pass_rate}}\n{b|%}`
          },
          rich: {
            a: {
              fontSize: 36,
              fontWeight: 'bold',
              color: '#303133'
            },
            b: {
              fontSize: 16,
              color: '#909399',
              padding: [5, 0, 0, 0]
            }
          }
        },
        emphasis: {
          label: {
            show: true
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: passRateData.value.passed, name: '通过', itemStyle: { color: '#67C23A' } },
          { value: passRateData.value.failed, name: '失败', itemStyle: { color: '#F56C6C' } },
          { value: passRateData.value.skipped, name: '跳过', itemStyle: { color: '#909399' } }
        ]
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  fetchPassRate()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 300px;
}

.legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
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
