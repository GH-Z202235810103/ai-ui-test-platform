<template>
  <div class="pie-chart-container">
    <div v-if="loading" class="loading-chart">
      <el-icon class="is-loading" :size="40"><loading /></el-icon>
      <div class="loading-text">加载中...</div>
    </div>
    <div v-else-if="error" class="error-chart">
      <el-icon :size="40" color="#F56C6C"><warning-filled /></el-icon>
      <div class="error-text">{{ error }}</div>
      <el-button size="small" @click="initChart" style="margin-top: 12px">
        重新加载
      </el-button>
    </div>
    <div v-else-if="total === 0" class="empty-chart">
      <el-empty description="暂无数据" :image-size="100" />
    </div>
    <div v-else ref="chartRef" class="chart-wrapper"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  passed: number
  failed: number
  skipped: number
  loading?: boolean
  error?: string
}>(), {
  loading: false,
  error: ''
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const total = computed(() => props.passed + props.failed + props.skipped)

const chartData = computed(() => {
  const data = [
    { value: props.passed, name: '通过', itemStyle: { color: '#67C23A' } },
    { value: props.failed, name: '失败', itemStyle: { color: '#F56C6C' } },
    { value: props.skipped, name: '跳过', itemStyle: { color: '#E6A23C' } },
  ]
  return data.filter(d => d.value > 0)
})

onMounted(() => {
  nextTick(() => {
    initChart()
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

watch(() => [props.passed, props.failed, props.skipped], () => {
  nextTick(() => {
    updateChart()
  })
})

function initChart() {
  if (!chartRef.value || total.value === 0 || props.loading || props.error) return

  try {
    if (chartInstance) {
      chartInstance.dispose()
    }
    chartInstance = echarts.init(chartRef.value)
    updateChart()
  } catch (err) {
    console.error('图表初始化失败:', err)
  }
}

function updateChart() {
  if (!chartInstance) {
    initChart()
    return
  }

  chartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const percent = total.value > 0 
          ? ((params.value / total.value) * 100).toFixed(1) 
          : 0
        return `${params.name}<br/>${params.value} 个 (${percent}%)`
      }
    },
    legend: {
      bottom: 0,
      itemGap: 20,
      textStyle: {
        fontSize: 12
      }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        },
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        }
      },
      labelLine: {
        show: false
      },
      data: chartData.value
    }]
  }, true)
}

function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}
</script>

<style scoped>
.pie-chart-container {
  width: 100%;
  min-height: 300px;
}

.loading-chart,
.error-chart,
.empty-chart {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.loading-text,
.error-text {
  margin-top: 12px;
  font-size: 14px;
  color: #909399;
}

.error-text {
  color: #F56C6C;
}

.chart-wrapper {
  width: 100%;
  height: 300px;
}

.is-loading {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .pie-chart-container,
  .loading-chart,
  .error-chart,
  .empty-chart,
  .chart-wrapper {
    height: 250px;
  }
}
</style>
