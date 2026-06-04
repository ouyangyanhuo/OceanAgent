<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { CheckCheck, Bell, GitFork, Link2, Sprout } from 'lucide-vue-next'

const props = defineProps({
  visible: { type: Boolean, default: false },
  anchorEl: { type: Object, default: null },
})

const emit = defineEmits(['close', 'update-count'])

const notifications = ref([])
const unreadCount = ref(0)
const panelStyle = ref({})
let pollTimer = null

const iconMap = {
  graph_expansion: GitFork,
  seed_node_created: Sprout,
  node_connected: Link2,
}

function updatePosition() {
  if (!props.anchorEl) return
  const rect = props.anchorEl.getBoundingClientRect()
  panelStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 8}px`,
    right: `${window.innerWidth - rect.right}px`,
    zIndex: 9999,
  }
}

watch(() => props.visible, (v) => {
  if (v) nextTick(updatePosition)
})

async function fetchNotifications() {
  try {
    const res = await fetch('/api/notification')
    const json = await res.json()
    if (json.success && json.data) {
      notifications.value = json.data.notifications || []
      unreadCount.value = json.data.unread_count || 0
      emit('update-count', unreadCount.value)
    }
  } catch {
    // silently ignore
  }
}

async function markAllRead() {
  try {
    await fetch('/api/notification/read-all', { method: 'POST' })
    notifications.value = notifications.value.map(n => ({ ...n, read: true }))
    unreadCount.value = 0
    emit('update-count', 0)
  } catch {
    // silently ignore
  }
}

async function markRead(id) {
  try {
    await fetch(`/api/notification/${id}/read`, { method: 'POST' })
    const target = notifications.value.find(n => n.id === id)
    if (target && !target.read) {
      target.read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
      emit('update-count', unreadCount.value)
    }
  } catch {
    // silently ignore
  }
}

function timeAgo(isoStr) {
  const diff = Date.now() - new Date(isoStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  return `${Math.floor(hours / 24)} 天前`
}

onMounted(() => {
  fetchNotifications()
  pollTimer = setInterval(fetchNotifications, 10000)
})

onUnmounted(() => {
  clearInterval(pollTimer)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="panel">
      <div v-if="visible" class="notification-panel" :style="panelStyle" @click.stop>
        <div class="notification-header">
          <span class="notification-title">通知</span>
          <button v-if="unreadCount > 0" class="notification-mark-all" @click="markAllRead">
            <CheckCheck :size="14" />
            全部已读
          </button>
        </div>
        <div class="notification-list">
          <div v-if="notifications.length === 0" class="notification-empty">
            <Bell :size="20" />
            <span>暂无通知</span>
          </div>
          <button
            v-for="n in notifications"
            :key="n.id"
            class="notification-item"
            :class="{ unread: !n.read }"
            @click="markRead(n.id)"
          >
            <div class="notification-icon">
              <component :is="iconMap[n.type] || GitFork" :size="16" />
            </div>
            <div class="notification-content">
              <div class="notification-item-title">{{ n.title }}</div>
              <div class="notification-item-message">{{ n.message }}</div>
              <div class="notification-time">{{ timeAgo(n.created_at) }}</div>
            </div>
            <div v-if="!n.read" class="notification-dot"></div>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
