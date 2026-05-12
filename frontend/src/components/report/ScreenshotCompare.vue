<template>
  <div class="screenshot-compare" v-if="expected || actual">
    <div class="screenshot-item" v-if="expected">
      <div class="screenshot-header">
        <h4>预期截图</h4>
        <el-tag type="success" size="small">Expected</el-tag>
      </div>
      <div class="screenshot-wrapper">
        <img
          :src="expected"
          loading="lazy"
          @error="onImgError($event, 'expected')"
          @click="previewImage(expected, '预期截图')"
          class="screenshot-img"
        />
        <div class="screenshot-overlay">
          <el-icon class="zoom-icon"><zoom-in /></el-icon>
          <span>点击查看大图</span>
        </div>
        <div v-if="imgErrors.expected" class="img-error">
          <el-icon :size="24"><picture-filled /></el-icon>
          <span>图片加载失败</span>
        </div>
      </div>
    </div>
    <div class="screenshot-item" v-if="actual">
      <div class="screenshot-header">
        <h4>实际截图</h4>
        <el-tag :type="hasDiff ? 'danger' : 'success'" size="small">
          {{ hasDiff ? '有差异' : 'Actual' }}
        </el-tag>
      </div>
      <div class="screenshot-wrapper">
        <img
          :src="actual"
          loading="lazy"
          @error="onImgError($event, 'actual')"
          @click="previewImage(actual, '实际截图')"
          class="screenshot-img"
        />
        <div class="screenshot-overlay">
          <el-icon class="zoom-icon"><zoom-in /></el-icon>
          <span>点击查看大图</span>
        </div>
        <div v-if="imgErrors.actual" class="img-error">
          <el-icon :size="24"><picture-filled /></el-icon>
          <span>图片加载失败</span>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="showPreview"
      :title="previewTitle"
      width="80%"
      top="5vh"
      destroy-on-close
    >
      <div class="preview-container">
        <img :src="previewUrl" class="preview-img" />
      </div>
      <template #footer>
        <el-button @click="downloadImage" type="primary">
          <el-icon><download /></el-icon>
          下载图片
        </el-button>
        <el-button @click="showPreview = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ZoomIn, PictureFilled, Download } from '@element-plus/icons-vue'

const props = defineProps<{
  expected: string | null
  actual: string | null
}>()

const imgErrors = ref({
  expected: false,
  actual: false
})

const showPreview = ref(false)
const previewUrl = ref('')
const previewTitle = ref('')

const hasDiff = computed(() => {
  return props.expected && props.actual && props.expected !== props.actual
})

function onImgError(e: Event, type: 'expected' | 'actual') {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
  imgErrors.value[type] = true
}

function previewImage(url: string, title: string) {
  previewUrl.value = url
  previewTitle.value = title
  showPreview.value = true
}

function downloadImage() {
  const link = document.createElement('a')
  link.href = previewUrl.value
  link.download = previewUrl.value.split('/').pop() || 'screenshot.png'
  link.click()
}
</script>

<style scoped>
.screenshot-compare {
  display: flex;
  gap: 20px;
  margin-top: 10px;
}

.screenshot-item {
  flex: 1;
  min-width: 0;
}

.screenshot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.screenshot-header h4 {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.screenshot-wrapper {
  position: relative;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
  background-color: #f5f7fa;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.screenshot-img {
  max-width: 100%;
  max-height: 300px;
  cursor: pointer;
  transition: transform 0.3s;
}

.screenshot-wrapper:hover .screenshot-img {
  transform: scale(1.02);
}

.screenshot-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
  cursor: pointer;
}

.screenshot-wrapper:hover .screenshot-overlay {
  opacity: 1;
}

.zoom-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.img-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #909399;
  padding: 20px;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  max-height: 70vh;
  overflow: auto;
}

.preview-img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

@media (max-width: 768px) {
  .screenshot-compare {
    flex-direction: column;
  }
}
</style>
