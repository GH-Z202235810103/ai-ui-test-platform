<template>
  <div class="nlp-generator">
    <el-card>
      <template #header>
        <span>自然语言生成测试用例</span>
      </template>
      
      <el-form :model="form" label-width="100px">
        <el-form-item label="用例描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="6"
            placeholder="请用自然语言描述测试场景，例如：&#10;1. 打开百度首页&#10;2. 在搜索框输入'Vue3'&#10;3. 点击搜索按钮&#10;4. 验证搜索结果包含Vue3相关内容"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleGenerate" :loading="generating">
            生成测试用例
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="generatedResult" style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>生成结果</span>
          <el-button type="success" size="small" @click="saveAsTestcase">保存为测试用例</el-button>
        </div>
      </template>
      
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用例名称">{{ generatedResult.name }}</el-descriptions-item>
        <el-descriptions-item label="用例类型">{{ generatedResult.type }}</el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 16px;">
        <h4>测试步骤：</h4>
        <el-table :data="generatedResult.steps" stripe>
          <el-table-column prop="step" label="步骤" width="60" />
          <el-table-column prop="action" label="操作" />
          <el-table-column prop="selector" label="选择器" />
          <el-table-column prop="value" label="值" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { generateFromNlp } from '../api/testcase'

const form = ref({
  description: ''
})
const generating = ref(false)
const generatedResult = ref<any>(null)

async function handleGenerate() {
  if (!form.value.description.trim()) {
    ElMessage.warning('请输入用例描述')
    return
  }
  
  generating.value = true
  try {
    const res = await generateFromNlp(form.value.description)
    if (res.success) {
      generatedResult.value = res.ai_generated
      ElMessage.success('生成成功')
    }
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    generating.value = false
  }
}

function saveAsTestcase() {
  ElMessage.info('请前往测试用例页面完善并保存')
}
</script>

<style scoped>
</style>
