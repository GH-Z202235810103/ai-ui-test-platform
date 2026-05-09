<template>
  <div ref="chartRef" style="width: 100%; height: 300px;"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  passed: number
  failed: number
  skipped: number
}>()

const chartRef = ref<HTMLElement>()

onMounted(() => { renderChart() })
watch(() => [props.passed, props.failed, props.skipped], () => { renderChart() })

function renderChart() {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      data: [
        { value: props.passed, name: '通过', itemStyle: { color: '#67C23A' } },
        { value: props.failed, name: '失败', itemStyle: { color: '#F56C6C' } },
        { value: props.skipped, name: '跳过', itemStyle: { color: '#E6A23C' } },
      ].filter(d => d.value > 0)
    }]
  })
}
</script>
