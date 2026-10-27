<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  isOpen: boolean
  title: string
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl'
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.isOpen) {
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

const maxWidthClass = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '2xl': 'max-w-2xl',
}[props.maxWidth || 'lg']
</script>

<template>
  <Teleport to="body">
    <div
      v-if="props.isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
    >
      <!-- Backdrop -->
      <div
        class="fixed inset-0 bg-black/60 transition-opacity"
        @click="emit('close')"
      />

      <!-- Dialog Card -->
      <div
        :class="[
          'relative w-full rounded-xl bg-white dark:bg-[#1e201d] border border-[#dfe7d6] dark:border-[#2f332b] shadow-xl transition-all z-10 flex flex-col max-h-[90vh]',
          maxWidthClass,
        ]"
      >
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-[#dfe7d6] dark:border-[#2f332b] px-5 py-3.5">
          <h2 class="text-sm font-semibold text-[#22261f] dark:text-[#e6eae2]">
            {{ props.title }}
          </h2>
          <button
            type="button"
            aria-label="Close dialog"
            class="rounded-lg p-1 text-[#5f6656] hover:bg-[#f3f7ed] dark:hover:bg-[#252922] hover:text-[#22261f] dark:hover:text-[#e6eae2] transition"
            @click="emit('close')"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="px-5 py-4 overflow-y-auto">
          <slot />
        </div>

        <!-- Footer -->
        <div v-if="$slots.footer" class="border-t border-[#dfe7d6] dark:border-[#2f332b] px-5 py-3 bg-[#f8faf4] dark:bg-[#161716] rounded-b-xl flex justify-end gap-2.5">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
