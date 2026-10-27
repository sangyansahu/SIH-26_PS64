import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const globalSearch = ref('')
  const unreadNotifications = ref(0)
  const isDemoMode = ref(false)
  const toastMessage = ref('')
  const toastKind = ref<'success' | 'error' | 'info'>('info')
  const isComplainantNotifOpen = ref(false)
  let toastTimer: ReturnType<typeof setTimeout> | undefined

  function toast(message: string, kind: 'success' | 'error' | 'info' = 'success') {
    toastMessage.value = message
    toastKind.value = kind
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { toastMessage.value = '' }, 3400)
  }

  return { globalSearch, unreadNotifications, isDemoMode, toastMessage, toastKind, isComplainantNotifOpen, toast }
})

