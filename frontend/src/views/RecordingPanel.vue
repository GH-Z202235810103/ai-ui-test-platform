<template>
  <div class="recording-panel">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>录制控制</span>
          </template>
          
          <el-form :model="recordingForm" label-width="80px">
            <el-form-item label="目标URL">
              <el-input v-model="recordingForm.url" placeholder="https://example.com" />
            </el-form-item>
            <el-form-item label="显示浏览器">
              <el-switch v-model="recordingForm.headless" active-text="隐藏" inactive-text="显示" />
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                @click="startRecording" 
                :loading="recording"
                :disabled="recording"
              >
                开始录制
              </el-button>
              <el-button 
                type="danger" 
                @click="stopRecording" 
                :loading="stopping"
                :disabled="!recording"
              >
                停止录制
              </el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="sessionId" class="session-info">
            <el-tag type="success">会话ID: {{ sessionId }}</el-tag>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>录制历史</span>
          </template>
          
          <el-table :data="recordings" v-loading="loadingHistory" stripe max-height="400">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="url" label="URL" show-overflow-tooltip />
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px;" v-if="recordedActions.length > 0">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>录制操作 ({{ recordedActions.length }} 步)</span>
          <el-button type="success" size="small" @click="replayRecording">回放</el-button>
        </div>
      </template>
      
      <el-table :data="recordedActions" stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="type" label="操作类型" width="120" />
        <el-table-column prop="selector" label="选择器" show-overflow-tooltip />
        <el-table-column prop="value" label="值" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { startRecording as apiStartRecording, stopRecording as apiStopRecording, getRecordings, deleteRecording } from '../api/recording'

const recordingForm = ref({
  url: 'https://www.baidu.com',
  headless: true
})
const recording = ref(false)
const stopping = ref(false)
const sessionId = ref('')
const recordedActions = ref<any[]>([])
const recordings = ref<any[]>([])
const loadingHistory = ref(false)

async function startRecording() {
  recording.value = true
  try {
    const res = await apiStartRecording(recordingForm.value.url, !recordingForm.value.headless)
    if (res.success) {
      sessionId.value = res.session_id
      ElMessage.success('录制已开始')
    }
  } catch (error) {
    ElMessage.error('启动录制失败')
    recording.value = false
  }
}

async function stopRecording() {
  stopping.value = true
  try {
    const res = await apiStopRecording(sessionId.value)
    if (res.success) {
      recordedActions.value = res.actions
      ElMessage.success(`录制完成，共 ${res.count} 步操作`)
    }
  } catch (error) {
    ElMessage.error('停止录制失败')
  } finally {
    stopping.value = false
    recording.value = false
  }
}

async function replayRecording() {
  try {
    ElMessage.info('回放功能开发中...')
  } catch (error) {
    ElMessage.error('回放失败')
  }
}

async function fetchRecordings() {
  loadingHistory.value = true
  try {
    const res = await getRecordings()
    if (res.success) {
      recordings.value = res.data
    }
  } catch (error) {
    console.error('获取录制历史失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定要删除该录制吗？', '提示', { type: 'warning' })
  try {
    await deleteRecording(id)
    ElMessage.success('删除成功')
    fetchRecordings()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchRecordings()
})
</script>

<style scoped>
.session-info {
  margin-top: 16px;
}
</style>
