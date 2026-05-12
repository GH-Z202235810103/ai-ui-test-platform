<template>
  <div class="task-list">
    <div class="toolbar">
      <el-select v-model="filterProject" placeholder="筛选项目" clearable style="width: 200px; margin-right: 12px;">
        <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>
      <el-button type="primary" @click="showDialog = true">新建任务</el-button>
    </div>

    <el-table :data="tasks" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column prop="execution_status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusMap[row.execution_status] || 'info'">
            {{ statusLabel[row.execution_status] || row.execution_status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="进度" width="120">
        <template #default="{ row }">
          <el-progress :percentage="row.progress || 0" :status="row.execution_status === 'success' ? 'success' : ''" />
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="开始时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.started_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="finished_at" label="结束时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.finished_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="handleStart(row.id)" :disabled="row.execution_status === 'running'">启动</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" title="新建任务" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="任务名称">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="form.type" placeholder="请选择类型">
            <el-option label="手动执行" value="manual" />
            <el-option label="定时执行" value="schedule" />
            <el-option label="触发执行" value="trigger" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属项目">
          <el-select v-model="form.project_id" placeholder="请选择项目">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTasks, createTask, updateTaskStatus, deleteTask } from '../api/task'
import { getProjects } from '../api/project'

const loading = ref(false)
const tasks = ref<any[]>([])
const projects = ref<any[]>([])
const filterProject = ref<number | null>(null)
const showDialog = ref(false)
const form = ref({
  name: '',
  type: 'manual',
  project_id: null as number | null
})

const statusMap: Record<string, string> = {
  pending: 'info',
  running: 'warning',
  success: 'success',
  failed: 'danger',
  stopped: 'info'
}

const statusLabel: Record<string, string> = {
  pending: '待执行',
  running: '执行中',
  success: '成功',
  failed: '失败',
  stopped: '已停止'
}

async function fetchTasks() {
  loading.value = true
  try {
    const res = await getTasks(filterProject.value || undefined)
    if (res.success) {
      tasks.value = res.data
    }
  } catch (error) {
    console.error('获取任务列表失败:', error)
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

async function handleSubmit() {
  try {
    await createTask({
      name: form.value.name,
      type: form.value.type,
      project_id: form.value.project_id || undefined
    })
    ElMessage.success('创建成功')
    showDialog.value = false
    form.value = { name: '', type: 'manual', project_id: null }
    fetchTasks()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

async function handleStart(id: number) {
  try {
    await updateTaskStatus(id, 'running')
    ElMessage.success('任务已启动')
    fetchTasks()
  } catch (error) {
    ElMessage.error('启动失败')
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定要删除该任务吗？', '提示', { type: 'warning' })
  try {
    await deleteTask(id)
    ElMessage.success('删除成功')
    fetchTasks()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

watch(filterProject, () => {
  fetchTasks()
})

onMounted(() => {
  fetchProjects()
  fetchTasks()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}
</style>
