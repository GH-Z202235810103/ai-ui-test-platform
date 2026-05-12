<template>
  <el-card class="summary-card" :body-style="{ padding: '20px' }">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><loading /></el-icon>
      <div class="loading-text">加载中...</div>
    </div>
    <div v-else-if="error" class="error-container">
      <el-icon :size="32" color="#F56C6C"><warning-filled /></el-icon>
      <div class="error-text">{{ error }}</div>
    </div>
    <div v-else-if="isEmpty" class="empty-container">
      <el-icon :size="32" color="#909399"><document-remove /></el-icon>
      <div class="empty-text">暂无数据</div>
    </div>
    <div v-else class="stat-content">
      <div class="stat-value" :style="{ color: color }">
        <count-up :end-val="numericValue" :duration="1" />
      </div>
      <div class="stat-label">{{ label }}</div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Loading, WarningFilled, DocumentRemove } from '@element-plus/icons-vue'
import CountUp from 'vue-countup-v3'

const props = withDefaults(defineProps<{
  value?: number | string
  label: string
  color?: string
  loading?: boolean
  error?: string
}>(), {
  value: 0,
  color: '#409EFF',
  loading: false,
  error: ''
})

const numericValue = computed(() => {
  if (typeof props.value === 'number') return props.value
  const num = parseFloat(props.value)
  return isNaN(num) ? 0 : num
})

const isEmpty = computed(() => {
  return !props.loading && !props.error && 
         (props.value === undefined || props.value === null || props.value === '')
})
</script>

<style scoped>
.summary-card {
  text-align: center;
  transition: all 0.3s;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80px;
}

.loading-text,
.error-text,
.empty-text {
  margin-top: 8px;
  font-size: 14px;
  color: #909399;
}

.error-text {
  color: #F56C6C;
}

.stat-content {
  animation: fadeIn 0.5s ease-in;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  transition: color 0.3s;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
</style>
