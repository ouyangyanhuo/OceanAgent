<script setup>
import { Anchor, Fish, MessageSquare, ShipWheel, Waves, Waypoints } from 'lucide-vue-next'

defineProps({
  agent: { type: Object, required: true },
})

const icons = [Waves, Waypoints, Fish, ShipWheel, MessageSquare, Anchor]
</script>

<template>
  <article class="agent-card" :class="`tone-${agent.tone}`">
    <div class="agent-icon">
      <component :is="icons[agent.name.length % icons.length]" :size="30" />
    </div>
    <div class="agent-body">
      <div class="agent-title">
        <h2>{{ agent.name }}</h2>
        <span>{{ agent.status }}</span>
      </div>
      <p>{{ agent.description }}</p>
      <div class="agent-footer">
        <div class="tags"><span v-for="tag in agent.tags" :key="tag">{{ tag }}</span></div>
        <button>调用</button>
      </div>
    </div>
  </article>
</template>
