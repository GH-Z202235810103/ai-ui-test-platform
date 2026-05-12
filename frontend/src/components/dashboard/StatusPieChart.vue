<template>
  <el-card :key="chartKey">
    <template #header>
      <span>测试状态分布</span>
    </template>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>

    <div v-else-if="error" class="error-container">
      <el-icon :size="40"><WarningFilled /></el-icon>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="total === 0" class="empty-container">
      <el-empty description="暂无测试数据" />
    </div>

    <!-- 始终存在的容器，用于挂载图表 -->
    <div ref="chartRef" class="chart-container" v-show="!loading && !error && total > 0"></div>

    <div v-show="!loading && !error && total > 0" class="legend">
        <div class="legend-item" @click="handleClick('pending')">
          <span class="legend-color" style="background: #909399;"></span>
          <span>待执行: {{ statusData.pending }}</span>
        </div>
        <div class="legend-item" @click="handleClick('running')">
          <span class="legend-color" style="background: #E6A23C;"></span>
          <span>执行中: {{ statusData.running }}</span>
        </div>
        <div class="legend-item" @click="handleClick('passed')">
          <span class="legend-color" style="background: #67C23A;"></span>
          <span>成功: {{ statusData.passed }}</span>
        </div>
        <div class="legend-item" @click="handleClick('failed')">
          <span class="legend-color" style="background: #F56C6C;"></span>
          <span>失败: {{ statusData.failed }}</span>
        </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onUpdated, nextTick, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import api from '../../api/index'

interface StatusData {
  pending: number
  running: number
  passed: number
  failed: number
}

const statusData = ref<StatusData>({
  pending: 0,
  running: 0,
  passed: 0,
  failed: 0
})

const loading = ref(true)
const error = ref('')
const chartRef = ref<HTMLElement>()
const router = useRouter()
const chartKey = ref(0)
let chartInstance: echarts.ECharts | null = null

// 监听 chartRef 的变化
watch(chartRef, (newVal) => {
  console.log('chartRef 变化:', newVal)
}, { immediate: true })

const total = computed(() => {
  return statusData.value.pending + statusData.value.running +
         statusData.value.passed + statusData.value.failed
})

const fetchStatusData = async () => {
  loading.value = true
  error.value = ''

  try {
    const { data } = await api.get('/v2/statistics')
    console.log('统计数据:', data)
    if (data.success) {
      const passRateStats = data.data.pass_rate_stats || {}
      statusData.value = {
        pending: passRateStats.skipped || 0,
        running: 0,
        passed: passRateStats.passed || 0,
        failed: passRateStats.failed || 0
      }
      console.log('状态数据:', statusData.value)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      console.log('nextTick完成，准备渲染饼图')
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 300)) // 等待更长时间
      renderChart()
    }
  } catch (e: any) {
    console.error('获取状态数据失败:', e)
    error.value = e.message || '获取状态数据失败'
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  // 确保组件已挂载且有数据
  if (!chartRef.value || total.value === 0) {
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

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '测试状态',
        type: 'pie',
        radius: ['40%', '60%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'center',
          formatter: () => {
            return `{a|${total.value}}\n{b|总数}`
          },
          rich: {
            a: {
              fontSize: 28,
              fontWeight: 'bold',
              color: '#303133'
            },
            b: {
              fontSize: 14,
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
          {
            value: statusData.value.pending,
            name: '待执行',
            itemStyle: { color: '#909399' },
            status: 'pending'
          },
          {
            value: statusData.value.running,
            name: '执行中',
            itemStyle: { color: '#E6A23C' },
            status: 'running'
          },
          {
            value: statusData.value.passed,
            name: '成功',
            itemStyle: { color: '#67C23A' },
            status: 'passed'
          },
          {
            value: statusData.value.failed,
            name: '失败',
            itemStyle: { color: '#F56C6C' },
            status: 'failed'
          }
        ]
      }
    ]
  }

  chartInstance.setOption(option)

  chartInstance.on('click', (params: any) => {
    if (params.data && params.data.status) {
      handleClick(params.data.status)
    }
  })
}

const handleClick = (status: string) => {
  router.push({
    path: '/testcases',
    query: { status }
  })
}

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  fetchStatusData()
  window.addEventListener('resize', handleResize)
})

onUpdated(() => {
  // 在组件更新后尝试重新渲染
  if (total.value > 0) {
    setTimeout(() => {
      renderChart()
    }, 100)
  }
})

onUnmounted(() => {
  chartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 250px;
}

.legend {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.legend-item:hover {
  background-color: #f5f7fa;
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
  height: 250px;
  color: #909399;
}

.error-container {
  color: #F56C6C;
}
</style>