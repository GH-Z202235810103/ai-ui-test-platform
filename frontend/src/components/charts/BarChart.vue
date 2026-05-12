<template>
  <div class="bar-chart-container">
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
    <div v-else-if="!data || data.length === 0" class="empty-chart">
      <el-empty description="暂无数据" :image-size="100" />
    </div>
    <div v-else ref="chartRef" class="chart-wrapper"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  data: { date: string; value: number }[]
  title: string
  color?: string
  loading?: boolean
  error?: string
}>(), {
  color: '#67C23A',
  loading: false,
  error: ''
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

function initChart() {
  if (!chartRef.value || !props.data.length || props.loading || props.error) return
  
  try {
    if (chartInstance) {
      chartInstance.dispose()
    }
    
    chartInstance = echarts.init(chartRef.value)
    chartInstance.setOption({
    title: { 
      text: props.title, 
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'normal' }
    },
    tooltip: { 
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0]
        return `${data.name}<br/>耗时: ${data.value}s`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: { 
      type: 'category', 
      data: props.data.map(d => d.date),
      axisLabel: { rotate: 45 }
    },
    yAxis: { 
      type: 'value', 
      axisLabel: { formatter: '{value}s' } 
    },
    series: [{
      data: props.data.map(d => d.value),
      type: 'bar',
      itemStyle: { 
        color: props.color || '#67C23A', 
        borderRadius: [4, 4, 0, 0] 
      },
      barMaxWidth: 40
    }]
  })
  } catch (err) {
    console.error('图表初始化失败:', err)
  }
}

function handleResize() {
  chartInstance?.resize()
}

watch(() => props.data, () => {
  nextTick(() => {
    initChart()
  })
}, { deep: true })

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
</script>

<style scoped>
.bar-chart-container {
  width: 100%;
  min-height: 350px;
}

.loading-chart,
.error-chart,
.empty-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 350px;
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
  height: 350px;
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
  .bar-chart-container,
  .loading-chart,
  .error-chart,
  .empty-chart,
  .chart-wrapper {
    height: 280px;
  }
}
</style>
