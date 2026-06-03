<script setup>
import { ref } from 'vue'
import { Anchor, Fish, MessageSquare, ShipWheel, Waves, Waypoints } from 'lucide-vue-next'

const props = defineProps({
  agent: { type: Object, required: true },
})

const emit = defineEmits(['invoke'])
const called = ref(false)
const icons = [Waves, Waypoints, Fish, ShipWheel, MessageSquare, Anchor]

function handleInvoke(e) {
  e.stopPropagation()
  if (called.value) return
  called.value = true
  emit('invoke', props.agent)
}
</script>

<template>
  <article class="agent-card" :class="[`tone-${agent.tone}`, { called }]" @click="handleInvoke">
    <div class="agent-icon">
      <component :is="icons[agent.name.length % icons.length]" :size="28" />
    </div>
    <div class="agent-body">
      <div class="agent-title">
        <h2>{{ agent.name }}</h2>
        <span class="agent-status">{{ agent.status }}</span>
      </div>
      <p>{{ agent.description }}</p>
      <div class="agent-footer">
        <div class="tags"><span v-for="tag in agent.tags" :key="tag">{{ tag }}</span></div>
        <button :class="{ 'btn-called': called }" @click.stop="handleInvoke">
          {{ called ? '已调用' : '调用' }}
        </button>
      </div>
    </div>
    <!-- Hover glow effect -->
    <div class="agent-glow"></div>
  </article>
</template>
