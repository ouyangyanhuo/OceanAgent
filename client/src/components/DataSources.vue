<script setup>
import { Cloud, RadioTower, Satellite, Ship, Waves } from 'lucide-vue-next'

defineProps({
  sources: { type: Array, required: true },
})

const sourceIcons = [RadioTower, Ship, Satellite, Cloud, Waves]
</script>

<template>
  <section class="panel compact-panel">
    <header class="panel-header">
      <h2><RadioTower :size="20" />海域数据接入</h2>
    </header>
    <div class="source-grid">
      <article v-for="(source, index) in sources" :key="source.name" :class="`tone-${source.tone}`">
        <component :is="sourceIcons[index % sourceIcons.length]" :size="28" />
        <div>
          <strong>{{ source.name }}</strong>
          <span>{{ source.status }}</span>
        </div>
        <b>{{ source.count }}</b>
      </article>
    </div>
  </section>
</template>
