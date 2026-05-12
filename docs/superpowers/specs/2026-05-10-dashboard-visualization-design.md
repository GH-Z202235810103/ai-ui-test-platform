# 仪表盘可视化模块设计文档

## 概述

在现有仪表盘页面的"任务状态分布"和"快速操作"模块下方，添加三个新的可视化模块，提升用户体验和数据洞察力。

## 目标

- 提供测试执行趋势的可视化展示
- 直观展示整体测试健康度
- 快速了解最新测试动态

## 模块设计

### 1. 测试执行趋势图

**位置**：全宽卡片，位于"快速操作"下方

**组件**：
- 文件：`frontend/src/components/dashboard/TrendChart.vue`
- 类型：ECharts 组合图表（折线图 + 柱状图）
- 复用：复用现有的 LineChart 和 BarChart 组件

**功能**：
- 时间范围选择器（7天/30天）
- 双Y轴设计：
  - 左Y轴：执行次数（折线图）
  - 右Y轴：通过率百分比（折线图）
  - 底部X轴：日期
- 失败用例数量柱状图
- 数据点悬停提示
- 图表缩放功能

**数据源**：
- API：`GET /api/v2/reports/trends/overview?days=7`
- 状态：✅ 已存在（endpoints.py:517）

**响应式**：
- 桌面端：全宽
- 移动端：全宽，高度自适应

### 2. 整体通过率环形图

**位置**：左侧卡片，与"最近测试活动时间线"并排

**组件**：
- 文件：`frontend/src/components/dashboard/PassRateRing.vue`
- 类型：ECharts 环形图
- 复用：复用现有的 PieChart 组件

**功能**：
- 中心显示：通过率百分比（大字体）
- 环形分段：
  - 通过（绿色，#67C23A）
  - 失败（红色，#F56C6C）
  - 跳过（灰色，#909399）
- 底部图例说明
- 悬停显示详细数据
- 点击跳转到报告列表

**数据源**：
- API：`GET /api/v2/statistics`
- 状态：⚠️ 需要扩展（endpoints.py:708）
- 扩展内容：添加 `pass_rate_stats` 字段

**响应式**：
- 桌面端：50%宽度
- 移动端：全宽

### 3. 最近测试活动时间线

**位置**：右侧卡片，与"整体通过率环形图"并排

**组件**：
- 文件：`frontend/src/components/dashboard/ActivityTimeline.vue`
- 类型：Element Plus Timeline 组件
- 新建：需要创建新组件

**功能**：
- 显示最近10条测试活动记录
- 每条记录包含：
  - 时间戳（相对时间，如"5分钟前"）
  - 用例名称
  - 状态标签（成功/失败/运行中）
  - 操作按钮（查看详情）
- 点击跳转到报告详情
- 自动刷新（可选，每30秒）

**数据源**：
- API：`GET /api/v2/recent-activities?limit=10`
- 状态：❌ 需要新建
- 实现位置：`backend/api/v2/endpoints.py`

**响应式**：
- 桌面端：50%宽度
- 移动端：全宽

## 布局结构

```
┌─────────────────────────────────────────────────────────┐
│                    统计卡片行                              │
│  [项目总数] [测试用例] [测试任务] [测试报告]                  │
└─────────────────────────────────────────────────────────┘

┌────────────────────────┬────────────────────────────────┐
│    任务状态分布          │        快速操作                  │
└────────────────────────┴────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              测试执行趋势图（全宽）                          │
│  [7天/30天选择器]                                          │
│  [折线图：执行次数 + 通过率]                                 │
│  [柱状图：失败用例数量]                                      │
└─────────────────────────────────────────────────────────┘

┌────────────────────────┬────────────────────────────────┐
│  整体通过率环形图        │    最近测试活动时间线              │
│  [环形图]               │    [时间线列表]                   │
│  [中心：通过率%]         │    - 5分钟前 | 用例A | 成功        │
│  [图例]                │    - 10分钟前 | 用例B | 失败        │
│                        │    - ...                        │
└────────────────────────┴────────────────────────────────┘
```

## 后端API设计

### 1. 扩展现有API：`/api/v2/statistics`

**位置**：`backend/api/v2/endpoints.py:708`

**扩展内容**：
```python
# 添加通过率统计
total_tests = db.query(TestReport).count()
passed_tests = db.query(TestReport).filter(TestReport.status == "passed").count()
failed_tests = db.query(TestReport).filter(TestReport.status == "failed").count()
skipped_tests = db.query(TestReport).filter(TestReport.status == "skipped").count()

pass_rate = round(passed_tests / total_tests * 100, 2) if total_tests > 0 else 0.0

# 在返回数据中添加
"pass_rate_stats": {
    "total": total_tests,
    "passed": passed_tests,
    "failed": failed_tests,
    "skipped": skipped_tests,
    "pass_rate": pass_rate
}
```

### 2. 新建API：`/api/v2/recent-activities`

**位置**：`backend/api/v2/endpoints.py`（新增）

**功能**：获取最近的测试活动记录

**参数**：
- `limit`：返回记录数量，默认10

**返回数据**：
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": 1,
        "testcase_name": "登录功能测试",
        "status": "passed",
        "executed_at": "2026-05-10T17:30:00",
        "duration": 5.2,
        "report_id": 123
      },
      ...
    ]
  }
}
```

**实现逻辑**：
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
        activities.append({
            "id": report.id,
            "testcase_name": report.summary.get("testcase_name", "N/A") if report.summary else "N/A",
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

## 前端组件实现

### 1. TrendChart.vue

**文件位置**：`frontend/src/components/dashboard/TrendChart.vue`

**依赖**：
- ECharts
- LineChart 组件
- BarChart 组件

**Props**：
- `days`：时间范围（7或30天）

**数据获取**：
```typescript
const fetchTrends = async () => {
  const { data } = await axios.get(`/api/v2/reports/trends/overview?days=${days.value}`)
  trendsData.value = data.data.trends
}
```

### 2. PassRateRing.vue

**文件位置**：`frontend/src/components/dashboard/PassRateRing.vue`

**依赖**：
- ECharts
- PieChart 组件

**数据获取**：
```typescript
const fetchPassRate = async () => {
  const { data } = await axios.get('/api/v2/statistics')
  passRateData.value = data.data.pass_rate_stats
}
```

### 3. ActivityTimeline.vue

**文件位置**：`frontend/src/components/dashboard/ActivityTimeline.vue`

**依赖**：
- Element Plus Timeline 组件
- Element Plus Tag 组件

**数据获取**：
```typescript
const fetchActivities = async () => {
  const { data } = await axios.get('/api/v2/recent-activities?limit=10')
  activities.value = data.data.activities
}
```

## Dashboard.vue 修改

**文件位置**：`frontend/src/views/Dashboard.vue`

**修改内容**：
1. 导入新组件
2. 添加新的布局行
3. 添加数据获取函数

**新增代码位置**：在第85行（`</el-row>` 后）添加新的模块

## 实施步骤

1. **后端实现**
   - 扩展 `/api/v2/statistics` API
   - 新建 `/api/v2/recent-activities` API

2. **前端组件创建**
   - 创建 `TrendChart.vue`
   - 创建 `PassRateRing.vue`
   - 创建 `ActivityTimeline.vue`

3. **Dashboard 集成**
   - 修改 `Dashboard.vue`
   - 导入新组件
   - 添加布局

4. **测试验证**
   - 启动前端服务
   - 访问仪表盘页面
   - 验证所有模块正常显示

## 成功标准

- ✅ 趋势图正确显示最近7天/30天的数据
- ✅ 环形图正确显示整体通过率
- ✅ 时间线正确显示最近10条活动记录
- ✅ 所有交互功能正常工作
- ✅ 响应式布局正常
- ✅ 没有控制台错误

## 风险评估

- **风险等级**：低
- **影响范围**：仅修改仪表盘页面，不影响其他功能
- **回滚方案**：如果出现问题，可以快速回滚到修改前的代码

## 时间估算

- 后端实现：30分钟
- 前端组件创建：60分钟
- Dashboard集成：20分钟
- 测试验证：20分钟
- **总计**：约2小时
