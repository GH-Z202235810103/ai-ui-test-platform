<template>
  <div class="step-table-container">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><loading /></el-icon>
      <div class="loading-text">加载中...</div>
    </div>
    <div v-else-if="error" class="error-container">
      <el-icon :size="40" color="#F56C6C"><warning-filled /></el-icon>
      <div class="error-text">{{ error }}</div>
    </div>
    <el-empty v-else-if="!steps || steps.length === 0" description="暂无步骤数据">
      <template #image>
        <el-icon :size="60" color="#909399"><document /></el-icon>
      </template>
    </el-empty>
    <div v-else>
      <el-table :data="paginatedSteps" stripe style="width: 100%" :row-class-name="getRowClassName">
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="expand-content">
            <div class="detail-section" v-if="row.step_desc">
              <h4>步骤描述</h4>
              <p>{{ row.step_desc }}</p>
            </div>
            <div class="detail-section error-section" v-if="row.error_message">
              <h4><el-icon><warning-filled /></el-icon> 错误信息</h4>
              <pre class="error-message">{{ row.error_message }}</pre>
            </div>
            <div class="detail-section" v-if="row.actual_screenshot || row.expected_screenshot">
              <h4>截图对比</h4>
              <ScreenshotCompare
                :expected="row.expected_screenshot"
                :actual="row.actual_screenshot"
              />
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="step_index" label="序号" width="80" align="center" />
      <el-table-column prop="step_name" label="步骤名称" min-width="200">
        <template #default="{ row }">
          <div class="step-name">
            <span>{{ row.step_name }}</span>
            <el-icon v-if="row.error_message" class="error-icon" :size="14"><warning-filled /></el-icon>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small" effect="dark">
            {{ statusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时" width="120" align="center">
        <template #default="{ row }">
          <span :class="{ 'slow-step': row.duration > 5000 }">
            {{ formatDuration(row.duration) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="截图" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.actual_screenshot || row.expected_screenshot" type="info" size="small">
            <el-icon><picture /></el-icon> 查看
          </el-tag>
          <span v-else class="no-screenshot">-</span>
        </template>
      </el-table-column>
    </el-table>
    <div v-if="steps.length > pageSize" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="steps.length"
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Document, WarningFilled, Picture, Loading } from '@element-plus/icons-vue'
import type { ReportStep } from '../../types/report'
import ScreenshotCompare from './ScreenshotCompare.vue'

const props = withDefaults(defineProps<{
  steps: ReportStep[]
  loading?: boolean
  error?: string
  pageSize?: number
}>(), {
  loading: false,
  error: '',
  pageSize: 10
})

const currentPage = ref(1)

const paginatedSteps = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return props.steps.slice(start, end)
})

function handlePageChange(page: number) {
  currentPage.value = page
}

function statusType(status: string) {
  return status === 'passed' ? 'success' : status === 'failed' ? 'danger' : 'warning'
}

function statusText(status: string) {
  return status === 'passed' ? '通过' : status === 'failed' ? '失败' : '跳过'
}

function formatDuration(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`
  }
  return `${(ms / 1000).toFixed(2)}s`
}

function getRowClassName({ row }: { row: ReportStep }): string {
  if (row.status === 'failed') return 'failed-row'
  if (row.status === 'skipped') return 'skipped-row'
  return ''
}
</script>

<style scoped>
.step-table-container {
  width: 100%;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
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

.expand-content {
  padding: 15px 20px;
  background-color: #fafafa;
}

.detail-section {
  margin-bottom: 15px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: #606266;
  font-weight: 600;
}

.detail-section p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}

.error-section h4 {
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 4px;
}

.error-message {
  margin: 0;
  padding: 10px;
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 4px;
  color: #f56c6c;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

.step-name {
  display: flex;
  align-items: center;
  gap: 6px;
}

.error-icon {
  color: #f56c6c;
}

.slow-step {
  color: #e6a23c;
  font-weight: 600;
}

.no-screenshot {
  color: #c0c4cc;
}

:deep(.failed-row) {
  background-color: #fef0f0 !important;
}

:deep(.skipped-row) {
  background-color: #fdf6ec !important;
}

:deep(.el-table__expanded-cell) {
  padding: 0 !important;
}
</style>
