import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/Dashboard.vue')
        },
        {
          path: 'projects',
          name: 'ProjectList',
          component: () => import('../views/ProjectList.vue')
        },
        {
          path: 'testcases',
          name: 'TestCaseList',
          component: () => import('../views/TestCaseList.vue')
        },
        {
          path: 'generate',
          name: 'NlpGenerator',
          component: () => import('../views/NlpGenerator.vue')
        },
        {
          path: 'tasks',
          name: 'TaskList',
          component: () => import('../views/TaskList.vue')
        },
        {
          path: 'reports',
          name: 'ReportList',
          component: () => import('../views/ReportList.vue')
        },
        {
          path: 'reports/trends',
          name: 'ProjectTrends',
          component: () => import('../views/ProjectTrends.vue')
        },
        {
          path: 'reports/:id',
          name: 'ReportDetail',
          component: () => import('../views/ReportDetail.vue'),
          props: true
        },
        {
          path: 'recording',
          name: 'RecordingPanel',
          component: () => import('../views/RecordingPanel.vue')
        },
        {
          path: 'visual',
          name: 'VisualLocator',
          component: () => import('../views/VisualLocator.vue')
        }
      ]
    }
  ]
})

export default router
