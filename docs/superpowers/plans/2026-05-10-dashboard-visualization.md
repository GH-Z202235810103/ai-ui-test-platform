# 仪表盘可视化模块实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在仪表盘页面添加三个可视化模块：测试执行趋势图、整体通过率环形图、最近测试活动时间线

**Architecture:** 扩展现有后端API，创建三个新的前端组件，集成到Dashboard页面

**Tech Stack:** FastAPI, Vue 3, TypeScript, ECharts, Element Plus

---

## 文件结构

**后端文件**：
- 修改：`backend/api/v2/endpoints.py` - 扩展statistics API，新建recent-activities API

**前端文件**：
- 创建：`frontend/src/components/dashboard/TrendChart.vue` - 趋势图组件
- 创建：`frontend/src/components/dashboard/PassRateRing.vue` - 通过率环形图组件
- 创建：`frontend/src/components/dashboard/ActivityTimeline.vue` - 活动时间线组件
- 修改：`frontend/src/views/Dashboard.vue` - 集成新组件

---

## Task 1: 扩展后端 statistics API

**Files:**
- Modify: `backend/api/v2/endpoints.py:708-733`

- [ ] **Step 1: 在 get_statistics 函数中添加通过率统计**

在 `backend/api/v2/endpoints.py` 的 `get_statistics` 函数中，在 `task_status_counts` 定义后添加：

```python
# 添加通过率统计
total_tests = db.query(TestReport).count()
passed_tests = db.query(TestReport).filter(TestReport.status == "passed").count()
failed_tests = db.query(TestReport).filter(TestReport.status == "failed").count()
skipped_tests = db.query(TestReport).filter(TestReport.status == "skipped").count()

pass_rate = round(passed_tests / total_tests * 100, 2) if total_tests > 0 else 0.0
```

- [ ] **Step 2: 在返回数据中添加 pass_rate_stats 字段**

修改 return 语句，添加 `pass_rate_stats`：

```python
return {
    "success": True,
    "data": {
        "projects": project_count,
        "testcases": testcase_count,
        "tasks": task_count,
        "reports": report_count,
        "recordings": recording_count,
        "visual_elements": visual_element_count,
        "task_status": task_status_counts,
        "pass_rate_stats": {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "pass_rate": pass_rate
        }
    }
}
```

- [ ] **Step 3: 测试 API**

启动后端服务，访问 `http://localhost:8001/api/v2/statistics`，验证返回数据包含 `pass_rate_stats` 字段。

---

## Task 2: 创建后端 recent-activities API

**Files:**
- Modify: `backend/api/v2/endpoints.py` (在 statistics API 后添加)

- [ ] **Step 1: 创建 get_recent_activities 函数**

在 `backend/api/v2/endpoints.py` 的 `get_statistics` 函数后添加：

```python
@router.get("/recent-activities")
async def get_recent_activities(limit: int = 10, db: Session = Depends(get_db)):
    """获取最近的测试活动记录"""
    reports = db.query(TestReport)\
        .order_by(TestReport.generated_at.desc())\
        .limit(limit)\
        .all()
    
    activities = []
    for report in reports:
        testcase_name = "N/A"
        if report.summary:
            if isinstance(report.summary, dict):
                testcase_name = report.summary.get("testcase_name", "N/A")
            elif isinstance(report.summary, str):
                try:
                    import json
                    summary_dict = json.loads(report.summary)
                    testcase_name = summary_dict.get("testcase_name", "N/A")
                except:
                    pass
        
        activities.append({
            "id": report.id,
            "testcase_name": testcase_name,
            "status": report.status,
            "executed_at": report.generated_at.isoformat() if report.generated_at else None,
            "duration": report.duration,
            "report_id": report.id
        })
    
    return {
        "success": True,
        "data": {
            "activities": activities
        }
    }
```

- [ ] **Step 2: 测试 API**

访问 `http://localhost:8001/api/v2/recent-activities?limit=10`，验证返回数据格式正确。

---

## Task 3: 创建 TrendChart 组件

**Files:**
- Create: `frontend/src/components/dashboard/TrendChart.vue`

- [ ] **Step 1: 创建 TrendChart.vue 文件**

创建文件 `frontend/src/components/dashboard/TrendChart.vue`：

```vue
<template>
  <el-card>
    <template #header>
      <div class="chart-header">
        <span>测试执行趋势</span>
        <el-radio-group v-model="selectedDays" size="small" @change="fetchTrends">
          <el-radio-button :value="7">最近7天</el-radio-button>
          <el-radio-button :value="30">最近30天</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    
    <div v-else-if="error" class="error-container">
      <el-icon :size="40"><WarningFilled /></el-icon>
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="trendsData.length === 0" class="empty-container">
      <el-empty description="暂无数据" />
    </div>
    
    <div v-else ref="chartRef" class="chart-container"></div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const selectedDays = ref(7)
const trendsData = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const fetchTrends = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const { data } = await axios.get(`/api/v2/reports/trends/overview?days=${selectedDays.value}`)
    if (data.success) {
      trendsData.value = data.data.trends || []
      await nextTick()
      renderChart()
    }
  } catch (e: any) {
    error.value = e.message || '获取趋势数据失败'
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  if (!chartRef.value || trendsData.value.length === 0) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const dates = trendsData.value.map(t => t.date)
  const executionCounts = trendsData.value.map(t => t.total)
  const passRates = trendsData.value.map(t => t.pass_rate)
  const failedCounts = trendsData.value.map(t => t.failed)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['执行次数', '通过率', '失败用例']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '执行次数',
        position: 'left'
      },
      {
        type: 'value',
        name: '通过率 (%)',
        position: 'right',
        min: 0,
        max: 100
      }
    ],
    series: [
      {
        name: '执行次数',
        type: 'line',
        data: executionCounts,
        smooth: true,
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '通过率',
        type: 'line',
        yAxisIndex: 1,
        data: passRates,
        smooth: true,
        itemStyle: {
          color: '#67C23A'
        }
      },
      {
        name: '失败用例',
        type: 'bar',
        data: failedCounts,
        itemStyle: {
          color: '#F56C6C'
        }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  fetchTrends()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})

watch(selectedDays, () => {
  fetchTrends()
})
</script>

<style scoped>
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #909399;
}

.error-container {
  color: #F56C6C;
}
</style>
```

- [ ] **Step 2: 验证组件创建成功**

确认文件已创建在正确位置。

---

## Task 4: 创建 PassRateRing 组件

**Files:**
- Create: `frontend/src/components/dashboard/PassRateRing.vue`

- [ ] **Step 1: 创建 PassRateRing.vue 文件**

创建文件 `frontend/src/components/dashboard/PassRateRing.vue`：

```vue
<template>
  <el-card>
    <template #header>
      <span>整体通过率</span>
    </template>
    
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    
    <div v-else-if="error" class="error-container">
      <el-icon :size="40"><WarningFilled /></el-icon>
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="!passRateData" class="empty-container">
      <el-empty description="暂无数据" />
    </div>
    
    <div v-else>
      <div ref="chartRef" class="chart-container"></div>
      <div class="legend">
        <div class="legend-item">
          <span class="legend-color" style="background: #67C23A;"></span>
          <span>通过: {{ passRateData.passed }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #F56C6C;"></span>
          <span>失败: {{ passRateData.failed }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #909399;"></span>
          <span>跳过: {{ passRateData.skipped }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import axios from 'axios'

interface PassRateStats {
  total: number
  passed: number
  failed: number
  skipped: number
  pass_rate: number
}

const passRateData = ref<PassRateStats | null>(null)
const loading = ref(false)
const error = ref('')
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const fetchPassRate = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const { data } = await axios.get('/api/v2/statistics')
    if (data.success) {
      passRateData.value = data.data.pass_rate_stats
      await nextTick()
      renderChart()
    }
  } catch (e: any) {
    error.value = e.message || '获取通过率数据失败'
  } finally {
    loading.value = false
  }
}

const renderChart = () => {
  if (!chartRef.value || !passRateData.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '测试结果',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'center',
          formatter: () => {
            return `{a|${passRateData.value!.pass_rate}}\n{b|%}`
          },
          rich: {
            a: {
              fontSize: 36,
              fontWeight: 'bold',
              color: '#303133'
            },
            b: {
              fontSize: 16,
              color: '#909399',
              padding: [5, 0, 0, 0]
            }
          }
        },
        emphasis: {
          label: {
            show: true
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: passRateData.value.passed, name: '通过', itemStyle: { color: '#67C23A' } },
          { value: passRateData.value.failed, name: '失败', itemStyle: { color: '#F56C6C' } },
          { value: passRateData.value.skipped, name: '跳过', itemStyle: { color: '#909399' } }
        ]
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  fetchPassRate()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 300px;
}

.legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #909399;
}

.error-container {
  color: #F56C6C;
}
</style>
```

- [ ] **Step 2: 验证组件创建成功**

确认文件已创建在正确位置。

---

## Task 5: 创建 ActivityTimeline 组件

**Files:**
- Create: `frontend/src/components/dashboard/ActivityTimeline.vue`

- [ ] **Step 1: 创建 ActivityTimeline.vue 文件**

创建文件 `frontend/src/components/dashboard/ActivityTimeline.vue`：

```vue
<template>
  <el-card>
    <template #header>
      <span>最近测试活动</span>
    </template>
    
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    
    <div v-else-if="error" class="error-container">
      <el-icon :size="40"><WarningFilled /></el-icon>
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="activities.length === 0" class="empty-container">
      <el-empty description="暂无测试活动" />
    </div>
    
    <div v-else class="timeline-container">
      <el-timeline>
        <el-timeline-item
          v-for="activity in activities"
          :key="activity.id"
          :timestamp="formatTime(activity.executed_at)"
          placement="top"
        >
          <el-card shadow="hover" class="activity-card" @click="viewDetail(activity.report_id)">
            <div class="activity-content">
              <div class="activity-name">{{ activity.testcase_name }}</div>
              <el-tag :type="getStatusType(activity.status)" size="small">
                {{ getStatusText(activity.status) }}
              </el-tag>
            </div>
            <div class="activity-duration" v-if="activity.duration">
              耗时: {{ activity.duration.toFixed(1) }}s
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import axios from 'axios'

interface Activity {
  id: number
  testcase_name: string
  status: string
  executed_at: string
  duration: number
  report_id: number
}

const activities = ref<Activity[]>([])
const loading = ref(false)
const error = ref('')
const router = useRouter()

const fetchActivities = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const { data } = await axios.get('/api/v2/recent-activities?limit=10')
    if (data.success) {
      activities.value = data.data.activities || []
    }
  } catch (e: any) {
    error.value = e.message || '获取活动数据失败'
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    passed: 'success',
    failed: 'danger',
    running: 'warning',
    pending: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    passed: '成功',
    failed: '失败',
    running: '运行中',
    pending: '待执行'
  }
  return texts[status] || status
}

const viewDetail = (reportId: number) => {
  router.push(`/reports/${reportId}`)
}

onMounted(() => {
  fetchActivities()
})
</script>

<style scoped>
.timeline-container {
  max-height: 400px;
  overflow-y: auto;
}

.activity-card {
  cursor: pointer;
  margin-bottom: 10px;
}

.activity-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.activity-name {
  font-weight: 500;
  color: #303133;
}

.activity-duration {
  font-size: 12px;
  color: #909399;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #909399;
}

.error-container {
  color: #F56C6C;
}
</style>
```

- [ ] **Step 2: 验证组件创建成功**

确认文件已创建在正确位置。

---

## Task 6: 集成组件到 Dashboard

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`

- [ ] **Step 1: 导入新组件**

在 `frontend/src/views/Dashboard.vue` 的 `<script setup>` 部分，添加导入：

```typescript
import TrendChart from '../components/dashboard/TrendChart.vue'
import PassRateRing from '../components/dashboard/PassRateRing.vue'
import ActivityTimeline from '../components/dashboard/ActivityTimeline.vue'
```

- [ ] **Step 2: 添加新的布局行**

在 `frontend/src/views/Dashboard.vue` 的模板中，在第二个 `</el-row>` 后（约第85行），添加新的模块：

```vue
<!-- 测试执行趋势图 -->
<el-row :gutter="20" style="margin-top: 20px;">
  <el-col :span="24">
    <TrendChart />
  </el-col>
</el-row>

<!-- 整体通过率和最近测试活动 -->
<el-row :gutter="20" style="margin-top: 20px;">
  <el-col :span="12">
    <PassRateRing />
  </el-col>
  <el-col :span="12">
    <ActivityTimeline />
  </el-col>
</el-row>
```

- [ ] **Step 3: 验证集成成功**

保存文件，确认没有语法错误。

---

## Task 7: 测试和验证

- [ ] **Step 1: 启动后端服务**

```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

- [ ] **Step 2: 启动前端服务**

```bash
cd frontend
npm run dev
```

- [ ] **Step 3: 访问仪表盘页面**

访问 `http://localhost:3001`（或前端服务显示的端口），点击"仪表盘"菜单。

- [ ] **Step 4: 验证所有模块正常显示**

检查：
- ✅ 趋势图正确显示（默认7天数据）
- ✅ 时间范围切换正常工作
- ✅ 通过率环形图正确显示
- ✅ 活动时间线正确显示
- ✅ 点击活动记录能跳转到详情页
- ✅ 没有控制台错误

- [ ] **Step 5: 提交代码**

```bash
git add .
git commit -m "feat: 添加仪表盘可视化模块

- 添加测试执行趋势图组件
- 添加整体通过率环形图组件
- 添加最近测试活动时间线组件
- 扩展后端 statistics API
- 新建后端 recent-activities API"
```

---

## 成功标准

- ✅ 所有API正常工作
- ✅ 所有组件正确渲染
- ✅ 交互功能正常
- ✅ 响应式布局正常
- ✅ 没有控制台错误
- ✅ 代码已提交

## 预计时间

- Task 1-2: 后端实现 (30分钟)
- Task 3-5: 前端组件创建 (60分钟)
- Task 6: Dashboard集成 (20分钟)
- Task 7: 测试验证 (20分钟)
- **总计**: 约2小时
