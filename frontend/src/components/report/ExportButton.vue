<template>
  <el-dropdown @command="handleExport">
    <el-button type="primary">
      导出报告 <el-icon class="el-icon--right"><arrow-down /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
        <el-dropdown-item command="html">导出 HTML</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ArrowDown } from '@element-plus/icons-vue'
import { exportReport } from '../../api/report'

const props = defineProps<{
  reportId: number
}>()

async function handleExport(format: string) {
  try {
    const blob = await exportReport(props.reportId, format as 'pdf' | 'html')
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `report_${props.reportId}.${format}`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出失败:', error)
  }
}
</script>
