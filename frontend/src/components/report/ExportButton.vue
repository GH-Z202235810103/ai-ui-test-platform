<template>
  <el-dropdown @command="handleExport" trigger="click" :disabled="exporting">
    <el-button type="primary" :loading="exporting">
      <el-icon v-if="!exporting"><download /></el-icon>
      {{ exporting ? '导出中...' : '导出报告' }}
      <el-icon class="el-icon--right" v-if="!exporting"><arrow-down /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="pdf" :disabled="exporting">
          <el-icon><document /></el-icon>
          导出 PDF
        </el-dropdown-item>
        <el-dropdown-item command="html" :disabled="exporting">
          <el-icon><document-copy /></el-icon>
          导出 HTML
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowDown, Download, Document, DocumentCopy } from '@element-plus/icons-vue'
import { exportReport } from '../../api/report'

const props = defineProps<{
  reportId: number
}>()

const exporting = ref(false)

async function handleExport(format: string) {
  if (exporting.value) return

  exporting.value = true
  const formatName = format === 'pdf' ? 'PDF' : 'HTML'

  try {
    ElMessage.info(`正在生成${formatName}报告，请稍候...`)

    const blob = await exportReport(props.reportId, format as 'pdf' | 'html')

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `report_${props.reportId}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success(`${formatName}报告导出成功`)
  } catch (error: any) {
    console.error('导出失败:', error)

    let errorMsg = '导出失败，请稍后重试'
    if (error.response) {
      if (error.response.status === 404) {
        errorMsg = '报告不存在或已被删除'
      } else if (error.response.status === 500) {
        errorMsg = '服务器错误，请稍后重试'
      } else if (error.response.data?.message) {
        errorMsg = error.response.data.message
      }
    } else if (error.message) {
      errorMsg = error.message
    }

    ElMessage.error(errorMsg)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.el-dropdown {
  margin-left: 12px;
}

.el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
