<script setup>
import { X } from 'lucide-vue-next'

const props = defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: '' },
  width: { type: String, default: '420px' },
})

const emit = defineEmits(['update:visible', 'close'])

function close() {
  emit('update:visible', false)
  emit('close')
}

function onOverlayClick(e) {
  if (e.target === e.currentTarget) close()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click="onOverlayClick">
        <div class="modal-container" :style="{ maxWidth: width }" @click.stop>
          <div class="modal-header">
            <h3>{{ title }}</h3>
            <button class="modal-close" @click="close"><X :size="18" /></button>
          </div>
          <div class="modal-body">
            <slot />
          </div>
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  background: rgba(2, 10, 22, 0.75);
  backdrop-filter: blur(8px);
}

.modal-container {
  width: 90%;
  background: rgba(7, 28, 52, 0.98);
  border: 1px solid rgba(39, 151, 255, 0.25);
  border-radius: 12px;
  box-shadow:
    0 0 40px rgba(0, 80, 180, 0.2),
    0 0 80px rgba(0, 40, 100, 0.15);
  display: flex;
  flex-direction: column;
  max-height: 85vh;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid rgba(39, 151, 255, 0.12);
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: #8fb9df;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.modal-body {
  padding: 18px 20px;
  overflow-y: auto;
  color: #b9d6ee;
  font-size: 13px;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 14px 20px;
  border-top: 1px solid rgba(39, 151, 255, 0.12);
}

/* ── 动画 ── */
.modal-enter-active {
  animation: modal-in 0.2s ease-out;
}

.modal-leave-active {
  animation: modal-in 0.15s ease-in reverse;
}

@keyframes modal-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-enter-active .modal-container {
  animation: modal-box-in 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.modal-leave-active .modal-container {
  animation: modal-box-in 0.15s ease-in reverse;
}

@keyframes modal-box-in {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
