<script setup lang="ts">
import { computed } from 'vue'
import {
  ChevronsUp,
  ChevronUp,
  Minus,
  ChevronDown
} from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    priority: string
    size?: 'sm' | 'md'
    variant?: 'inline' | 'tag' | 'pill'
  }>(),
  {
    size: 'sm',
    variant: 'inline',
  }
)

const config = computed(() => {
  switch (props.priority?.toLowerCase()) {
    case 'critical':
      return {
        icon: ChevronsUp,
        iconColor: 'text-red-700 dark:text-[#f87171]',
        textColor: 'text-red-700 dark:text-[#f87171] font-semibold',
        tagBg: 'bg-red-50 text-red-700 border-red-200 dark:bg-[#341416] dark:text-[#f87171] dark:border-[#521c20]',
        dotColor: 'bg-red-700 dark:bg-[#c72e2e]',
        label: 'Critical',
      }
    case 'high':
      return {
        icon: ChevronUp,
        iconColor: 'text-[#b86f00] dark:text-[#facc15]',
        textColor: 'text-[#854d0e] dark:text-[#facc15] font-medium',
        tagBg: 'bg-[#fef9c3] text-[#854d0e] border-[#fef08a] dark:bg-[#282614] dark:text-[#facc15] dark:border-[#423f1f]',
        dotColor: 'bg-[#b86f00] dark:bg-[#facc15]',
        label: 'High',
      }
    case 'medium':
      return {
        icon: Minus,
        iconColor: 'text-[#7eaa3b] dark:text-[#b8ee82]',
        textColor: 'text-[#465f29] dark:text-[#b8ee82] font-medium',
        tagBg: 'bg-[#f0f6e9] text-[#465f29] border-[#d8e5cb] dark:bg-[#1a2417] dark:text-[#b8ee82] dark:border-[#2a3c23]',
        dotColor: 'bg-[#7eaa3b] dark:bg-[#b8ee82]',
        label: 'Medium',
      }
    case 'low':
      return {
        icon: ChevronDown,
        iconColor: 'text-[#5f6656] dark:text-[#989e92]',
        textColor: 'text-[#5f6656] dark:text-[#989e92] font-normal',
        tagBg: 'bg-[#f3f7ed] text-[#5f6656] border-[#dfe7d6] dark:bg-[#1e201d] dark:text-[#989e92] dark:border-[#2f332b]',
        dotColor: 'bg-[#5f6656] dark:bg-[#989e92]',
        label: 'Low',
      }
    default:
      return {
        icon: Minus,
        iconColor: 'text-[#5f6656] dark:text-[#989e92]',
        textColor: 'text-[#5f6656] dark:text-[#989e92] font-normal',
        tagBg: 'bg-[#f3f7ed] text-[#5f6656] border-[#dfe7d6] dark:bg-[#1e201d] dark:text-[#989e92] dark:border-[#2f332b]',
        dotColor: 'bg-[#5f6656] dark:bg-[#989e92]',
        label: props.priority || 'Medium',
      }
  }
})
</script>

<template>
  <!-- Inline Modern Style (Linear / GitHub / VS Code style) -->
  <span
    v-if="variant === 'inline'"
    class="inline-flex items-center gap-1.5 text-xs whitespace-nowrap"
  >
    <component
      :is="config.icon"
      :class="['shrink-0', size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4', config.iconColor]"
      aria-hidden="true"
    />
    <span :class="config.textColor">{{ config.label }}</span>
  </span>

  <!-- Flat Micro-Tag Style (VS Code Editor tag style) -->
  <span
    v-else-if="variant === 'tag'"
    :class="[
      'inline-flex items-center gap-1.5 rounded border whitespace-nowrap text-xs font-medium',
      size === 'sm' ? 'px-2 py-0.5' : 'px-2.5 py-1',
      config.tagBg,
    ]"
  >
    <component
      :is="config.icon"
      :class="['shrink-0', size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5', config.iconColor]"
      aria-hidden="true"
    />
    <span>{{ config.label }}</span>
  </span>

  <!-- Refined Pill Style -->
  <span
    v-else
    :class="[
      'inline-flex items-center gap-1.5 rounded-full border whitespace-nowrap text-xs font-medium',
      size === 'sm' ? 'px-2 py-0.5' : 'px-2.5 py-0.5',
      config.tagBg,
    ]"
  >
    <span :class="['w-1.5 h-1.5 rounded-full shrink-0', config.dotColor]" />
    <span>{{ config.label }}</span>
  </span>
</template>
