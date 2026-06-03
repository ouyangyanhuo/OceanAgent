import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fallbackDashboard, fetchDashboard as apiFetchDashboard } from '../services/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  const data = ref(fallbackDashboard)
  const loading = ref(false)

  async function fetch() {
    loading.value = true
    try {
      data.value = await apiFetchDashboard()
    } finally {
      loading.value = false
    }
  }

  return { data, loading, fetch }
})
