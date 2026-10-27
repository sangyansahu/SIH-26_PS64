import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/api/client'
import type { NotificationItem } from '@/types'

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<NotificationItem[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)

  async function fetchNotifications(unreadOnly = false) {
    loading.value = true
    try {
      const response = await apiClient.get('/notifications', {
        params: { unread_only: unreadOnly }
      })
      notifications.value = response.data.notifications
      unreadCount.value = response.data.unread_count
    } catch (err) {
      // Ignore
    } finally {
      loading.value = false
    }
  }

  async function markAsRead(id: number) {
    try {
      await apiClient.patch(`/notifications/${id}/read`)
      const found = notifications.value.find(n => n.id === id)
      if (found && !found.is_read) {
        found.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    } catch (err) {
      // Ignore
    }
  }

  async function markAllRead() {
    try {
      await apiClient.post('/notifications/read-all')
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
    } catch (err) {
      // Ignore
    }
  }

  async function checkDeadlines() {
    try {
      await apiClient.post('/notifications/check-deadlines')
      await fetchNotifications()
    } catch (err) {
      // Ignore
    }
  }

  return {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    markAsRead,
    markAllRead,
    checkDeadlines,
  }
})
