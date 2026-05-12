<template>
  <div class="visual-locator">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>视觉模板管理</span>
          </template>
          
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="handleFileChange"
          >
            <el-button type="primary">上传模板图片</el-button>
          </el-upload>
          
          <div v-if="uploadForm.element_name" style="margin-top: 16px;">
            <el-form :model="uploadForm" label-width="80px">
              <el-form-item label="元素名称">
                <el-input v-model="uploadForm.element_name" placeholder="按钮名称" />
              </el-form-item>
              <el-form-item label="元素类型">
                <el-select v-model="uploadForm.element_type" placeholder="请选择">
                  <el-option label="按钮" value="button" />
                  <el-option label="输入框" value="input" />
                  <el-option label="链接" value="link" />
                  <el-option label="图片" value="image" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="success" @click="uploadTemplate" :loading="uploading">保存模板</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <el-table :data="templates" v-loading="loadingTemplates" stripe style="margin-top: 16px;">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="element_type" label="类型" width="100" />
            <el-table-column prop="usage_count" label="使用次数" width="100" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="handleDelete(row.name)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>视觉定位测试</span>
          </template>
          
          <el-form :model="locateForm" label-width="80px">
            <el-form-item label="截图上传">
              <el-upload
                ref="locateUploadRef"
                :auto-upload="false"
                :show-file-list="false"
                accept="image/*"
                :on-change="handleLocateFileChange"
              >
                <el-button>选择截图</el-button>
              </el-upload>
              <span v-if="locateForm.screenshot" style="margin-left: 12px;">已选择: {{ locateForm.screenshot.name }}</span>
            </el-form-item>
            <el-form-item label="目标元素">
              <el-select v-model="locateForm.element_name" placeholder="请选择要定位的元素">
                <el-option v-for="t in templates" :key="t.id" :label="t.name" :value="t.name" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleLocate" :loading="locating">开始定位</el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="locateResult" class="locate-result">
            <el-alert
              :title="locateResult.found ? '定位成功' : '定位失败'"
              :type="locateResult.found ? 'success' : 'error'"
              show-icon
            >
              <template v-if="locateResult.found">
                <p>坐标: ({{ locateResult.x }}, {{ locateResult.y }})</p>
                <p>置信度: {{ (locateResult.confidence * 100).toFixed(1) }}%</p>
              </template>
            </el-alert>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getVisualTemplates, createVisualTemplate, deleteVisualTemplate, locateElement } from '../api/visual'

const templates = ref<any[]>([])
const loadingTemplates = ref(false)
const uploading = ref(false)
const locating = ref(false)

const uploadForm = ref({
  element_name: '',
  element_type: 'button',
  file: null as File | null
})

const locateForm = ref({
  screenshot: null as File | null,
  element_name: ''
})

const locateResult = ref<any>(null)

async function fetchTemplates() {
  loadingTemplates.value = true
  try {
    const res = await getVisualTemplates()
    if (res.success) {
      templates.value = res.templates
    }
  } catch (error) {
    console.error('获取模板列表失败:', error)
  } finally {
    loadingTemplates.value = false
  }
}

function handleFileChange(file: any) {
  uploadForm.value.file = file.raw
  uploadForm.value.element_name = file.name.replace(/\.[^/.]+$/, '')
}

async function uploadTemplate() {
  if (!uploadForm.value.file) {
    ElMessage.warning('请先选择图片')
    return
  }
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    formData.append('element_name', uploadForm.value.element_name)
    formData.append('element_type', uploadForm.value.element_type)
    
    const res = await createVisualTemplate(formData)
    if (res.success) {
      ElMessage.success('模板创建成功')
      uploadForm.value = { element_name: '', element_type: 'button', file: null }
      fetchTemplates()
    }
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    uploading.value = false
  }
}

async function handleDelete(name: string) {
  await ElMessageBox.confirm('确定要删除该模板吗？', '提示', { type: 'warning' })
  try {
    await deleteVisualTemplate(name)
    ElMessage.success('删除成功')
    fetchTemplates()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

function handleLocateFileChange(file: any) {
  locateForm.value.screenshot = file.raw
}

async function handleLocate() {
  if (!locateForm.value.screenshot || !locateForm.value.element_name) {
    ElMessage.warning('请选择截图和目标元素')
    return
  }
  
  locating.value = true
  try {
    const res = await locateElement(locateForm.value.screenshot, locateForm.value.element_name)
    if (res.success) {
      locateResult.value = res
    }
  } catch (error) {
    ElMessage.error('定位失败')
  } finally {
    locating.value = false
  }
}

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.locate-result {
  margin-top: 16px;
}
</style>
