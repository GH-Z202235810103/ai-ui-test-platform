<template>
  <el-table :data="steps" stripe style="width: 100%">
    <el-table-column type="expand">
      <template #default="{ row }">
        <div style="padding: 15px;">
          <p v-if="row.step_desc"><strong>描述:</strong> {{ row.step_desc }}</p>
          <p v-if="row.error_message" style="color: #F56C6C;"><strong>错误:</strong> {{ row.error_message }}</p>
          <ScreenshotCompare
            v-if="row.actual_screenshot || row.expected_screenshot"
            :expected="row.expected_screenshot"
            :actual="row.actual_screenshot"
          />
        </div>
      </template>
    </el-table-column>
    <el-table-column prop="step_index" label="序号" width="80" />
    <el-table-column prop="step_name" label="步骤名称" />
    <el-table-column prop="status" label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="duration" label="耗时(ms)" width="120" />
  </el-table>
</template>

<script setup lang="ts">
import type { ReportStep } from '../../types/report'
import ScreenshotCompare from './ScreenshotCompare.vue'

defineProps<{
  steps: ReportStep[]
}>()

function statusType(status: string) {
  return status === 'passed' ? 'success' : status === 'failed' ? 'danger' : 'warning'
}

function statusText(status: string) {
  return status === 'passed' ? '通过' : status === 'failed' ? '失败' : '跳过'
}
</script>
