<template>
  <div class="testcase-list">
    <div class="toolbar">
      <el-select v-model="filterProject" placeholder="筛选项目" clearable style="width: 200px; margin-right: 12px;">
        <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>
      <el-button type="primary" @click="showDialog = true">新建用例</el-button>
      
      <template v-if="selectedIds.length > 0">
        <el-divider direction="vertical" />
        <span class="selected-info">已选 {{ selectedIds.length }} 项</span>
        <el-button type="warning" @click="showBatchProjectDialog = true">批量修改项目</el-button>
        <el-button type="success" @click="handleBatchExecute">批量执行</el-button>
        <el-button type="danger" @click="handleBatchDelete">批量删除</el-button>
      </template>
    </div>

    <el-table 
      ref="tableRef"
      :data="testcases" 
      v-loading="loading" 
      stripe
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="用例名称" />
      <el-table-column prop="project_name" label="所属项目" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.project_id" size="small">{{ getProjectName(row.project_id) }}</el-tag>
          <span v-else class="text-gray">未分配</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusMap[row.status] || 'info'">{{ row.status || '草稿' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="version" label="版本" width="80" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="handleExecute(row.id)">执行</el-button>
          <el-button size="small" @click="editTestcase(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" :title="editingTestcase ? '编辑用例' : '新建用例'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用例名称">
          <el-input v-model="form.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" placeholder="请输入用例描述" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" placeholder="请选择类型">
            <el-option label="UI测试" value="ui" />
            <el-option label="API测试" value="api" />
            <el-option label="E2E测试" value="e2e" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属项目">
          <el-select v-model="form.project_id" placeholder="请选择项目" clearable>
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试步骤">
          <el-input v-model="stepsJson" type="textarea" :rows="6" placeholder="JSON格式的测试步骤" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBatchProjectDialog" title="批量修改所属项目" width="400px">
      <el-form label-width="80px">
        <el-form-item label="目标项目">
          <el-select v-model="batchProjectId" placeholder="请选择项目" clearable style="width: 100%;">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-alert 
            :title="`将修改 ${selectedIds.length} 个用例的所属项目`" 
            type="info" 
            :closable="false"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatchProjectDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchUpdateProject" :loading="batchLoading">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showExecutionConfigDialog" title="执行参数配置" width="500px">
      <el-form :model="executionConfig" label-width="120px">
        <el-form-item label="无头模式">
          <el-switch v-model="executionConfig.headless" />
          <span style="margin-left: 12px; color: #909399; font-size: 12px;">
            {{ executionConfig.headless ? '后台运行，不显示浏览器窗口' : '显示浏览器窗口' }}
          </span>
        </el-form-item>
        
        <el-form-item label="执行超时时间">
          <el-input-number 
            v-model="executionConfig.timeout" 
            :min="5" 
            :max="300" 
            :step="5"
            style="width: 150px;"
          />
          <span style="margin-left: 12px; color: #909399; font-size: 12px;">秒</span>
        </el-form-item>
        
        <el-form-item label="重试次数">
          <el-input-number 
            v-model="executionConfig.retryCount" 
            :min="0" 
            :max="10" 
            :step="1"
            style="width: 150px;"
          />
          <span style="margin-left: 12px; color: #909399; font-size: 12px;">失败后自动重试次数</span>
        </el-form-item>
        
        <el-form-item label="截图质量">
          <el-slider 
            v-model="executionConfig.screenshotQuality" 
            :min="10" 
            :max="100" 
            :step="10"
            show-stops
            show-input
            style="width: 100%;"
          />
          <span style="color: #909399; font-size: 12px;">截图压缩质量，数值越大质量越高</span>
        </el-form-item>
        
        <el-form-item label="启用截图">
          <el-switch v-model="executionConfig.screenshotEnabled" />
          <span style="margin-left: 12px; color: #909399; font-size: 12px;">
            {{ executionConfig.screenshotEnabled ? '执行测试时将保存页面截图' : '执行测试时不保存截图' }}
          </span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showExecutionConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmExecution">
          {{ pendingBatchExecution ? '开始批量执行' : '开始执行' }}
        </el-button>
      </template>
    </el-dialog>

    <ExecutionProgress
      v-model="showExecutionProgress"
      :execution-id="currentExecutionId"
      @completed="handleExecutionCompleted"
    />

    <BatchExecutionProgress
      v-model="showBatchProgress"
      :execution-ids="batchExecutionIds"
      @view-detail="handleViewExecutionDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getTestCases, 
  createTestCase, 
  updateTestCase, 
  deleteTestCase, 
  executeTestCase,
  executeBatch,
  type ExecutionResult 
} from '../api/testcase'
import { getProjects } from '../api/project'
import ExecutionProgress from '../components/execution/ExecutionProgress.vue'
import BatchExecutionProgress from '../components/execution/BatchExecutionProgress.vue'

const tableRef = ref()
const loading = ref(false)
const testcases = ref<any[]>([])
const projects = ref<any[]>([])
const filterProject = ref<number | null>(null)
const showDialog = ref(false)
const editingTestcase = ref<any>(null)
const form = ref({
  name: '',
  description: '',
  type: '',
  project_id: null as number | null,
  script_data: { steps: [] }
})
const stepsJson = ref('')

const selectedIds = ref<number[]>([])
const showBatchProjectDialog = ref(false)
const batchProjectId = ref<number | null>(null)
const batchLoading = ref(false)

const showExecutionProgress = ref(false)
const currentExecutionId = ref<string | null>(null)
const showBatchProgress = ref(false)
const batchExecutionIds = ref<any[]>([])

const showExecutionConfigDialog = ref(false)
const executionConfig = ref({
  headless: true,
  timeout: 30,
  retryCount: 3,
  screenshotQuality: 80,
  screenshotEnabled: true
})
const pendingExecutionId = ref<number | null>(null)
const pendingBatchExecution = ref(false)

const statusMap: Record<string, string> = {
  draft: '',
  pending: 'warning',
  passed: 'success',
  failed: 'danger'
}

async function fetchTestcases() {
  loading.value = true
  try {
    const res = await getTestCases(filterProject.value || undefined)
    if (res.success) {
      testcases.value = res.data
    }
  } catch (error) {
    console.error('获取用例列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchProjects() {
  try {
    const res = await getProjects()
    if (res.success) {
      projects.value = res.data
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

function getProjectName(projectId: number) {
  const project = projects.value.find(p => p.id === projectId)
  return project?.name || '未知项目'
}

function handleSelectionChange(selection: any[]) {
  selectedIds.value = selection.map(item => item.id)
}

function editTestcase(testcase: any) {
  editingTestcase.value = testcase
  form.value = {
    name: testcase.name || '',
    description: testcase.description || '',
    type: testcase.type || '',
    project_id: testcase.project_id,
    script_data: testcase.script_data || { steps: [] }
  }
  stepsJson.value = JSON.stringify(form.value.script_data.steps, null, 2)
  showDialog.value = true
}

async function handleSubmit() {
  try {
    form.value.script_data = { steps: JSON.parse(stepsJson.value || '[]') }
    if (editingTestcase.value) {
      await updateTestCase(editingTestcase.value.id, {
        ...form.value,
        project_id: form.value.project_id || undefined
      })
      ElMessage.success('更新成功')
    } else {
      await createTestCase({
        ...form.value,
        project_id: form.value.project_id || undefined
      })
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    editingTestcase.value = null
    resetForm()
    fetchTestcases()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleExecute(id: number) {
  pendingExecutionId.value = id
  pendingBatchExecution.value = false
  showExecutionConfigDialog.value = true
}

function handleExecutionCompleted(result: ExecutionResult) {
  ElMessage.success(`执行完成: ${result.testcase_name}`)
  fetchTestcases()
}

async function handleBatchExecute() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  
  pendingBatchExecution.value = true
  showExecutionConfigDialog.value = true
}

function handleViewExecutionDetail(execution: any) {
  currentExecutionId.value = execution.execution_id
  showExecutionProgress.value = true
}

async function handleConfirmExecution() {
  showExecutionConfigDialog.value = false
  
  if (pendingBatchExecution.value) {
    await ElMessageBox.confirm(
      `确定要批量执行 ${selectedIds.value.length} 个用例吗？`, 
      '批量执行', 
      { type: 'info' }
    )
    
    try {
      ElMessage.info('正在启动批量执行...')
      const res = await executeBatch(selectedIds.value, executionConfig.value)
      if (res.success) {
        batchExecutionIds.value = res.execution_ids
        showBatchProgress.value = true
        ElMessage.success(res.message)
        selectedIds.value = []
        tableRef.value?.clearSelection()
      }
    } catch (error) {
      ElMessage.error('批量执行失败')
    }
  } else if (pendingExecutionId.value) {
    try {
      ElMessage.info('正在启动执行...')
      const res = await executeTestCase(pendingExecutionId.value, executionConfig.value)
      if (res.success) {
        currentExecutionId.value = res.execution_id
        showExecutionProgress.value = true
        ElMessage.success('执行已开始，请查看执行进度')
      }
    } catch (error) {
      ElMessage.error('执行失败')
    }
  }
  
  pendingExecutionId.value = null
  pendingBatchExecution.value = false
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定要删除该用例吗？', '提示', { type: 'warning' })
  try {
    await deleteTestCase(id)
    ElMessage.success('删除成功')
    fetchTestcases()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

async function handleBatchUpdateProject() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  
  batchLoading.value = true
  let successCount = 0
  let failCount = 0
  
  for (const id of selectedIds.value) {
    try {
      const testcase = testcases.value.find(t => t.id === id)
      if (testcase) {
        await updateTestCase(id, {
          name: testcase.name,
          description: testcase.description,
          type: testcase.type,
          project_id: batchProjectId.value || undefined,
          script_data: testcase.script_data
        })
        successCount++
      }
    } catch (error) {
      failCount++
    }
  }
  
  batchLoading.value = false
  showBatchProjectDialog.value = false
  
  if (successCount > 0) {
    ElMessage.success(`成功修改 ${successCount} 个用例`)
  }
  if (failCount > 0) {
    ElMessage.warning(`${failCount} 个用例修改失败`)
  }
  
  selectedIds.value = []
  tableRef.value?.clearSelection()
  fetchTestcases()
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  
  await ElMessageBox.confirm(
    `确定要删除选中的 ${selectedIds.value.length} 个用例吗？此操作不可恢复！`, 
    '批量删除', 
    { type: 'warning' }
  )
  
  let successCount = 0
  for (const id of selectedIds.value) {
    try {
      await deleteTestCase(id)
      successCount++
    } catch (error) {
      console.error(`删除用例 ${id} 失败`)
    }
  }
  
  ElMessage.success(`成功删除 ${successCount} 个用例`)
  selectedIds.value = []
  tableRef.value?.clearSelection()
  fetchTestcases()
}

function resetForm() {
  form.value = { name: '', description: '', type: '', project_id: null, script_data: { steps: [] } }
  stepsJson.value = ''
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

watch(filterProject, () => {
  fetchTestcases()
})

onMounted(() => {
  fetchProjects()
  fetchTestcases()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.selected-info {
  color: #409EFF;
  font-weight: 500;
  margin-right: 8px;
}
.text-gray {
  color: #909399;
}
</style>
