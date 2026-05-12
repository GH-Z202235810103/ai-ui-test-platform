<template>
  <el-card :key="chartKey">
    <template #header>
      <div class="chart-header">
        <span>测试执行趋势</span>
        <el-radio-group v-model="selectedDays" size="small" @change="fetchTrends">
          <el-radio-button :value="7">最近7天</el-radio-button>
          <el-radio-button :value="30">最近30天</el-radio-button>
        </el-radio-group>
      </div>
    </template>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>

    <div v-else-if="error" class="error-container">
      <el-icon :size="40"><WarningFilled /></el-icon>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="trendsData.length === 0" class="empty-container">
      <el-empty description="暂无数据" />
    </div>

    <!-- 始终存在的容器，用于挂载图表 -->
    <div ref="chartRef" class="chart-container" v-show="!loading && !error && trendsData.length > 0"></div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onUpdated, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import api from '../../api/index'

const selectedDays = ref(7)
const trendsData = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const chartRef = ref<HTMLElement>()
const chartKey = ref(0)
let chartInstance: echarts.ECharts | null = null

// 监听 chartRef 的变化
watch(chartRef, (newVal) => {
  console.log('chartRef 变化:', newVal)
}, { immediate: true })

const fetchTrends = async () => {
  loading.value = true
  error.value = ''

  try {
    const { data } = await api.get(`/v2/reports/trends/overview?days=${selectedDays.value}`)
    console.log('趋势数据:', data)
    if (data.success) {
      trendsData.value = data.data.trends || []
      console.log('处理后的趋势数据:', trendsData.value)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      console.log('nextTick完成，准备渲染趋势图')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 300)) // 等待更长时间
      renderChart()
    }
  } catch (e: any) {
    console.error('获取趋势数据失败:', e)
    error.value = e.message || '获取趋势数据失败'
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  // 确保组件已挂载且有数据
  if (!chartRef.value || trendsData.value.length === 0) {
    return
  }

  // 销毁现有图表实例
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }

  // 确保容器可见
  chartRef.value.style.display = 'block'

  // 初始化图表
  chartInstance = echarts.init(chartRef.value)

  const dates = trendsData.value.map(t => t.date)
  const executionCounts = trendsData.value.map(t => t.total)
  const passRates = trendsData.value.map(t => t.pass_rate)
  const failedCounts = trendsData.value.map(t => t.failed)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['执行次数', '通过率', '失败用例']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '执行次数',
        position: 'left'
      },
      {
        type: 'value',
        name: '通过率 (%)',
        position: 'right',
        min: 0,
        max: 100
      }
    ],
    series: [
      {
        name: '执行次数',
        type: 'line',
        data: executionCounts,
        smooth: true,
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '通过率',
        type: 'line',
        yAxisIndex: 1,
        data: passRates,
        smooth: true,
        itemStyle: {
          color: '#67C23A'
        }
      },
      {
        name: '失败用例',
        type: 'bar',
        data: failedCounts,
        itemStyle: {
          color: '#F56C6C'
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  fetchTrends()
  window.addEventListener('resize', handleResize)
})

onUpdated(() => {
  // 在组件更新后尝试重新渲染
  if (trendsData.value.length > 0) {
    setTimeout(() => {
      renderChart()
    }, 100)
  }
})

onUnmounted(() => {
  chartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})

watch(selectedDays, () => {
  fetchTrends()
})
</script>

<style scoped>
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #909399;
}

.error-container {
  color: #F56C6C;
}
</style>