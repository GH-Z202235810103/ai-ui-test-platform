<template>
  <div ref="chartRef" style="width: 100%; height: 350px;"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  data: { date: string; value: number }[]
  title: string
  color?: string
}>()

const chartRef = ref<HTMLElement>()

onMounted(() => { renderChart() })
watch(() => props.data, () => { renderChart() }, { deep: true })

function renderChart() {
  if (!chartRef.value || !props.data.length) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: props.title, left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.data.map(d => d.date) },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{
      data: props.data.map(d => d.value),
      type: 'line',
      smooth: true,
      itemStyle: { color: props.color || '#409EFF' },
      areaStyle: { opacity: 0.1 }
    }]
  })
}
</script>
