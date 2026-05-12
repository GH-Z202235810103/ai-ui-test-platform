<template>
  <div class="project-list">
    <div class="toolbar">
      <el-button type="primary" @click="showDialog = true">新建项目</el-button>
    </div>

    <el-table :data="projects" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="base_url" label="基础URL" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '活跃' : '归档' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="editProject(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" :title="editingProject ? '编辑项目' : '新建项目'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" placeholder="请输入项目描述" />
        </el-form-item>
        <el-form-item label="基础URL">
          <el-input v-model="form.base_url" placeholder="https://example.com" />
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjects, createProject, updateProject, deleteProject } from '../api/project'

const loading = ref(false)
const projects = ref<any[]>([])
const showDialog = ref(false)
const editingProject = ref<any>(null)
const form = ref({
  name: '',
  description: '',
  base_url: ''
})

async function fetchProjects() {
  loading.value = true
  try {
    const res = await getProjects()
    if (res.success) {
      projects.value = res.data
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

function editProject(project: any) {
  editingProject.value = project
  form.value = {
    name: project.name || '',
    description: project.description || '',
    base_url: project.base_url || ''
  }
  showDialog.value = true
}

async function handleSubmit() {
  try {
    if (editingProject.value) {
      await updateProject(editingProject.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await createProject(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    editingProject.value = null
    form.value = { name: '', description: '', base_url: '' }
    fetchProjects()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定要删除该项目吗？', '提示', { type: 'warning' })
  try {
    await deleteProject(id)
    ElMessage.success('删除成功')
    fetchProjects()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}
</style>
