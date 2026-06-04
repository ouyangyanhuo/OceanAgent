<script setup>
import { Anchor, Fish, MessageSquare, ShipWheel, Waves, Waypoints } from 'lucide-vue-next'

const props = defineProps({
  agent: { type: Object, required: true },
})

const icons = [Waves, Waypoints, Fish, ShipWheel, MessageSquare, Anchor]
</script>

<template>
  <article class="agent-card" :class="[`tone-${agent.tone}`]">
    <!-- Outer bezel shell -->
    <div class="agent-bezel">
      <!-- Inner core -->
      <div class="agent-core">
        <div class="agent-header">
          <div class="agent-icon">
            <component :is="icons[agent.name.length % icons.length]" :size="22" />
          </div>
          <div class="agent-meta">
            <span class="agent-eyebrow">{{ agent.status }}</span>
            <h2>{{ agent.name }}</h2>
          </div>
        </div>
        <p class="agent-desc">{{ agent.description }}</p>
        <div class="agent-footer">
          <div class="tags"><span v-for="tag in agent.tags" :key="tag">{{ tag }}</span></div>
        </div>
      </div>
    </div>
    <!-- Hover glow effect -->
    <div class="agent-glow"></div>
  </article>
</template>
