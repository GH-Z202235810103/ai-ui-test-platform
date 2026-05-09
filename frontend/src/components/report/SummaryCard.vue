<template>
  <el-card class="summary-card" :body-style="{ padding: '20px' }">
    <div class="stat-value" :style="{ color: color }">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  value: number | string
  label: string
  color?: string
}>()
</script>

<style scoped>
.summary-card { text-align: center; }
.stat-value { font-size: 32px; font-weight: bold; }
.stat-label { font-size: 14px; color: #909399; margin-top: 8px; }
</style>
