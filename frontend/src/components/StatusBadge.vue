<script setup lang="ts">
import { computed } from 'vue'
import {
  Inbox,
  Clock,
  AlertTriangle,
  HelpCircle,
  ArrowUpRight,
  CheckCircle2,
  Check
} from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    status: string
    size?: 'sm' | 'md'
    variant?: 'inline' | 'tag' | 'pill'
  }>(),
  {
    size: 'sm',
    variant: 'inline',
  }
)

const badgeConfig = computed(() => {
  switch (props.status) {
    case 'Received':
      return {
        icon: Inbox,
        dot: 'bg-slate-400 dark:bg-[#989898]',
        iconColor: 'text-slate-500 dark:text-[#989898]',
        textColor: 'text-slate-700 dark:text-[#cccccc]',
        tagBg: 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-[#2d2d2d] dark:text-[#cccccc] dark:border-[#3e3e42]',
      }
    case 'Under Review':
      return {
        icon: Clock,
        dot: 'bg-[#b86f00] dark:bg-[#fdd878]',
        iconColor: 'text-[#b86f00] dark:text-[#fdd878]',
        textColor: 'text-[#7a4800] dark:text-[#fdd878]',
        tagBg: 'bg-[#fef9ec] text-[#7a4800] border-[#fce7b0] dark:bg-[#2b2515] dark:text-[#fdd878] dark:border-[#42391e]',
      }
    case 'Action Required':
      return {
        icon: AlertTriangle,
        dot: 'bg-[#c2410c] dark:bg-[#ff944d]',
        iconColor: 'text-[#c2410c] dark:text-[#ff944d]',
        textColor: 'text-[#9a3412] dark:text-[#ff944d]',
        tagBg: 'bg-[#fff5ee] text-[#9a3412] border-[#ffddc7] dark:bg-[#301f17] dark:text-[#ff944d] dark:border-[#4a2e20]',
      }
    case 'Awaiting Response':
      return {
        icon: HelpCircle,
        dot: 'bg-sky-600 dark:bg-[#70d7ff]',
        iconColor: 'text-sky-700 dark:text-[#70d7ff]',
        textColor: 'text-sky-900 dark:text-[#70d7ff]',
        tagBg: 'bg-sky-50 text-sky-900 border-sky-200 dark:bg-[#142633] dark:text-[#70d7ff] dark:border-[#1d3d52]',
      }
    case 'Escalated':
      return {
        icon: ArrowUpRight,
        dot: 'bg-rose-700 dark:bg-[#ff6b6b]',
        iconColor: 'text-rose-700 dark:text-[#ff6b6b]',
        textColor: 'text-rose-900 dark:text-[#ff6b6b] font-semibold',
        tagBg: 'bg-rose-50 text-rose-900 border-rose-200 dark:bg-[#381a1c] dark:text-[#ff6b6b] dark:border-[#522428]',
      }
    case 'Disposed':
      return {
        icon: CheckCircle2,
        dot: 'bg-[#5e9a2e] dark:bg-[#b8ee82]',
        iconColor: 'text-[#5e9a2e] dark:text-[#b8ee82]',
        textColor: 'text-[#2e5917] dark:text-[#b8ee82]',
        tagBg: 'bg-[#f0f5e8] text-[#2e5917] border-[#dfe7d6] dark:bg-[#1f2817] dark:text-[#b8ee82] dark:border-[#2f3f1e]',
      }
    case 'Closed':
      return {
        icon: Check,
        dot: 'bg-zinc-400 dark:bg-[#989e92]',
        iconColor: 'text-zinc-600 dark:text-[#989e92]',
        textColor: 'text-zinc-800 dark:text-[#989e92]',
        tagBg: 'bg-zinc-100 text-zinc-800 border-zinc-200 dark:bg-[#1e201d] dark:text-[#989e92] dark:border-[#2f332b]',
      }
    default:
      return {
        icon: Inbox,
        dot: 'bg-slate-400 dark:bg-[#989898]',
        iconColor: 'text-slate-500 dark:text-[#989898]',
        textColor: 'text-slate-700 dark:text-[#cccccc]',
        tagBg: 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-[#2d2d2d] dark:text-[#cccccc] dark:border-[#3e3e42]',
      }
  }
})
</script>

<template>
  <!-- Inline Modern Style (Linear / VS Code style: Illuminated status dot + label) -->
  <span
    v-if="variant === 'inline'"
    class="inline-flex items-center gap-2 text-xs whitespace-nowrap"
  >
    <span :class="['rounded-full shrink-0', size === 'sm' ? 'w-2 h-2' : 'w-2.5 h-2.5', badgeConfig.dot]" />
    <span :class="badgeConfig.textColor">{{ props.status }}</span>
  </span>

  <!-- Flat Micro-Tag Style (Structured rectangular tag) -->
  <span
    v-else-if="variant === 'tag'"
    :class="[
      'inline-flex items-center gap-1.5 rounded border whitespace-nowrap text-xs font-medium',
      size === 'sm' ? 'px-2 py-0.5' : 'px-2.5 py-1',
      badgeConfig.tagBg,
    ]"
  >
    <span :class="['w-1.5 h-1.5 rounded-full shrink-0', badgeConfig.dot]" />
    <span>{{ props.status }}</span>
  </span>

  <!-- Refined Pill Style -->
  <span
    v-else
    :class="[
      'inline-flex items-center gap-1.5 rounded-full border whitespace-nowrap text-xs font-medium',
      size === 'sm' ? 'px-2.5 py-0.5' : 'px-3 py-1',
      badgeConfig.tagBg,
    ]"
  >
    <span :class="['w-1.5 h-1.5 rounded-full shrink-0', badgeConfig.dot]" />
    <span>{{ props.status }}</span>
  </span>
</template>
