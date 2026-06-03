import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/agents',
  },
  {
    path: '/agents',
    name: 'agents',
    component: () => import('../views/AgentSearchPage.vue'),
  },
  {
    path: '/graph',
    name: 'graph',
    component: () => import('../views/GraphPage.vue'),
  },
  {
    path: '/qa',
    name: 'qa',
    component: () => import('../views/EcoQaPage.vue'),
  },
  {
    path: '/fishery',
    name: 'fishery',
    component: () => import('../views/FisheryAssessmentPage.vue'),
  },
  {
    path: '/route',
    name: 'route',
    component: () => import('../views/RouteOptimizationPage.vue'),
  },
  {
    path: '/buoy',
    name: 'buoy',
    component: () => import('../views/BuoyDiagnosticsPage.vue'),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
