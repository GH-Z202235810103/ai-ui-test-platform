<template>
  <div class="layout">
    <el-container>
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <h1>AI UI测试平台</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          
          <el-sub-menu index="project">
            <template #title>
              <el-icon><Folder /></el-icon>
              <span>项目管理</span>
            </template>
            <el-menu-item index="/projects">项目列表</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="testcase">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>测试用例</span>
            </template>
            <el-menu-item index="/testcases">用例列表</el-menu-item>
            <el-menu-item index="/generate">自然语言生成</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="task">
            <template #title>
              <el-icon><List /></el-icon>
              <span>测试任务</span>
            </template>
            <el-menu-item index="/tasks">任务列表</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="report">
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>测试报告</span>
            </template>
            <el-menu-item index="/reports">报告列表</el-menu-item>
            <el-menu-item index="/reports/trends">趋势分析</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="recording">
            <template #title>
              <el-icon><VideoCamera /></el-icon>
              <span>录制回放</span>
            </template>
            <el-menu-item index="/recording">录制管理</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="visual">
            <template #title>
              <el-icon><Picture /></el-icon>
              <span>AI视觉定位</span>
            </template>
            <el-menu-item index="/visual">模板管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header class="header">
          <div class="header-content">
            <span class="page-title">{{ pageTitle }}</span>
          </div>
        </el-header>
        
        <el-main class="main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  HomeFilled, 
  Folder, 
  Document, 
  List, 
  DataAnalysis, 
  VideoCamera, 
  Picture 
} from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/dashboard': '仪表盘',
    '/projects': '项目列表',
    '/testcases': '测试用例',
    '/generate': '自然语言生成',
    '/tasks': '测试任务',
    '/reports/trends': '测试趋势',
    '/recording': '录制回放',
    '/visual': 'AI视觉定位'
  }
  return titles[route.path] || 'AI UI自动化测试平台'
})
</script>

<style scoped>
.layout {
  height: 100vh;
  overflow: hidden;
}
.layout .el-container {
  height: 100%;
}
.sidebar {
  background-color: #304156;
  height: 100%;
  overflow-y: auto;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.logo h1 {
  font-size: 18px;
  margin: 0;
}
.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  height: 60px;
}
.header-content {
  padding: 0 20px;
}
.page-title {
  font-size: 18px;
  font-weight: 500;
}
.main {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
