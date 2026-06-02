<script setup>
import { ClipboardList } from 'lucide-vue-next'

defineProps({
  tasks: { type: Array, required: true },
})
</script>

<template>
  <section class="panel compact-panel">
    <header class="panel-header">
      <h2><ClipboardList :size="20" />任务动态</h2>
      <button>查看更多 ›</button>
    </header>
    <div class="timeline">
      <article v-for="task in tasks" :key="task.time + task.title" :class="`tone-${task.tone}`">
        <time>{{ task.time }}</time>
        <span class="node"></span>
        <p>{{ task.title }}</p>
        <b>{{ task.status }}</b>
      </article>
    </div>
  </section>
</template>
