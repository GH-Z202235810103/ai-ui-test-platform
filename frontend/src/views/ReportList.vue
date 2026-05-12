<template>
  <div class="report-list">
    <h2 class="page-title">测试报告列表</h2>

    <div class="filter-section">
      <el-select
        v-model="filterProject"
        placeholder="选择项目"
        clearable
        style="width: 200px"
      >
        <el-option
          v-for="p in projects"
          :key="p.id"
          :label="p.name"
          :value="p.id"
        />
      </el-select>

      <el-select
        v-model="filterStatus"
        placeholder="选择状态"
        clearable
        style="width: 150px; margin-left: 12px"
      >
        <el-option label="成功" value="success" />
        <el-option label="失败" value="failed" />
        <el-option label="运行中" value="running" />
      </el-select>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="margin-left: 12px"
        value-format="YYYY-MM-DD"
      />

      <el-button type="primary" style="margin-left: 12px" @click="handleSearch">
        搜索
      </el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>

    <el-table
      :data="paginatedReports"
      v-loading="loading"
      stripe
      :default-sort="{ prop: 'generated_at', order: 'descending' }"
      @sort-change="handleSortChange"
    >
      <el-table-column prop="id" label="报告ID" width="100" sortable />

      <el-table-column prop="task_name" label="测试用例名称" min-width="180">
        <template #default="{ row }">
          {{ row.task_name || `测试任务 #${row.task_id}` }}
        </template>
      </el-table-column>

      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="total_count" label="总步骤数" width="100" sortable>
        <template #default="{ row }">
          {{ row.total_count || 0 }}
        </template>
      </el-table-column>

      <el-table-column prop="pass_count" label="通过数" width="90">
        <template #default="{ row }">
          <span class="pass-count">{{ row.pass_count || 0 }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="fail_count" label="失败数" width="90">
        <template #default="{ row }">
          <span class="fail-count">{{ row.fail_count || 0 }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="pass_rate" label="通过率" width="120" sortable>
        <template #default="{ row }">
          <span :class="getPassRateClass(row.pass_rate)">
            {{ formatPassRate(row.pass_rate) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column prop="generated_at" label="生成时间" width="180" sortable>
        <template #default="{ row }">
          {{ formatDate(row.generated_at) }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleViewDetail(row.id)">
            查看详情
          </el-button>
          <el-dropdown style="margin-left: 8px" @command="(cmd: string) => handleExport(row.id, cmd)">
            <el-button size="small">
              导出<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pdf">导出PDF</el-dropdown-item>
                <el-dropdown-item command="html">导出HTML</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <div v-if="!loading && filteredReports.length === 0" class="empty-tip">
      <el-empty description="暂无测试报告数据" />
    </div>

    <div class="pagination-section" v-if="filteredReports.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredReports.length"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { getReportsList, exportReport } from '../api/report'
import { getProjects } from '../api/project'

const router = useRouter()
const loading = ref(false)
const reports = ref<any[]>([])
const projects = ref<any[]>([])

const filterProject = ref<number | null>(null)
const filterStatus = ref<string | null>(null)
const dateRange = ref<[string, string] | null>(null)

const currentPage = ref(1)
const pageSize = ref(10)

const sortProp = ref('generated_at')
const sortOrder = ref<'ascending' | 'descending'>('descending')

const statusMap: Record<string, string> = {
  success: 'success',
  failed: 'danger',
  running: 'warning',
  pending: 'info'
}

const statusLabelMap: Record<string, string> = {
  success: '成功',
  failed: '失败',
  running: '运行中',
  pending: '待执行'
}

function getStatusType(status: string): string {
  return statusMap[status] || 'info'
}

function getStatusLabel(status: string): string {
  return statusLabelMap[status] || status
}

function formatPassRate(rate: number): string {
  if (rate === null || rate === undefined) return '-'
  return `${(rate * 100).toFixed(1)}%`
}

function getPassRateClass(rate: number): string {
  if (rate === null || rate === undefined) return ''
  return rate >= 0.8 ? 'pass-rate-high' : 'pass-rate-low'
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const filteredReports = computed(() => {
  let result = [...reports.value]

  if (filterProject.value) {
    result = result.filter((r) => r.project_id === filterProject.value)
  }

  if (filterStatus.value) {
    result = result.filter((r) => r.status === filterStatus.value)
  }

  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    endDate.setHours(23, 59, 59, 999)
    result = result.filter((r) => {
      const reportDate = new Date(r.generated_at)
      return reportDate >= startDate && reportDate <= endDate
    })
  }

  if (sortProp.value) {
    result.sort((a, b) => {
      const aVal = a[sortProp.value]
      const bVal = b[sortProp.value]
      if (aVal === null || aVal === undefined) return 1
      if (bVal === null || bVal === undefined) return -1
      const compare = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
      return sortOrder.value === 'ascending' ? compare : -compare
    })
  }

  return result
})

const paginatedReports = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredReports.value.slice(start, end)
})

async function fetchReports() {
  loading.value = true
  try {
    const res = await getReportsList()
    if (res.success) {
      reports.value = res.data || []
    }
  } catch (error) {
    console.error('获取报告列表失败:', error)
    ElMessage.error('获取报告列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchProjects() {
  try {
    const res = await getProjects()
    if (res.success) {
      projects.value = res.data || []
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

function handleSearch() {
  currentPage.value = 1
}

function handleReset() {
  filterProject.value = null
  filterStatus.value = null
  dateRange.value = null
  currentPage.value = 1
}

function handleSortChange({ prop, order }: { prop: string; order: string | null }) {
  sortProp.value = prop
  sortOrder.value = order === 'ascending' ? 'ascending' : 'descending'
}

function handleViewDetail(id: number) {
  router.push(`/reports/${id}`)
}

async function handleExport(reportId: number, format: string) {
  try {
    ElMessage.info('正在导出报告...')
    const blob = await exportReport(reportId, format as 'pdf' | 'html')
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `report_${reportId}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出报告失败:', error)
    ElMessage.error('导出报告失败')
  }
}

onMounted(() => {
  fetchProjects()
  fetchReports()
})
</script>

<style scoped>
.report-list {
  padding: 20px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.filter-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.pass-count {
  color: #67c23a;
  font-weight: 500;
}

.fail-count {
  color: #f56c6c;
  font-weight: 500;
}

.pass-rate-high {
  color: #67c23a;
  font-weight: 600;
}

.pass-rate-low {
  color: #f56c6c;
  font-weight: 600;
}

.empty-tip {
  padding: 40px 0;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-section .el-select,
  .filter-section .el-date-picker {
    width: 100% !important;
    margin-left: 0 !important;
    margin-bottom: 8px;
  }
}
</style>
