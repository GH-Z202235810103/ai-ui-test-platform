import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/reports/trends'
    },
    {
      path: '/reports/trends',
      name: 'ProjectTrends',
      component: () => import('../views/ProjectTrends.vue')
    },
    {
      path: '/reports/:id',
      name: 'ReportDetail',
      component: () => import('../views/ReportDetail.vue'),
      props: true
    }
  ]
})

export default router
