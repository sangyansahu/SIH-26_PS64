<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import EmptyState from '@/components/EmptyState.vue'
import {
  Bell,
  CheckCheck,
  Clock,
  GitCompare,
  AlertTriangle,
  ArrowRight,
  ShieldAlert,
} from 'lucide-vue-next'

const notifStore = useNotificationsStore()
const router = useRouter()
const unreadOnly = ref(false)

onMounted(() => {
  notifStore.fetchNotifications(unreadOnly.value)
})

function toggleUnread() {
  notifStore.fetchNotifications(unreadOnly.value)
}

function handleNotificationClick(notif: any) {
  notifStore.markAsRead(notif.id)
  if (notif.related_complaint_id) {
    router.push(`/complaints/${notif.related_complaint_id}`)
  } else if (notif.notification_type === 'overlap_detected') {
    router.push('/overlaps')
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-slate-900 dark:text-[#d4d4d4]">
          Notifications
        </h1>
        <p class="text-xs text-slate-500 dark:text-[#989898] mt-0.5">
          Updates for related case overlaps, deadlines, and assignments
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="inline-flex items-center gap-1.5 rounded border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-50 dark:hover:bg-[#37373d] transition"
          @click="notifStore.checkDeadlines()"
        >
          <Clock class="w-3.5 h-3.5 text-slate-500 dark:text-[#989898]" />
          Check Deadlines
        </button>

        <button
          v-if="notifStore.unreadCount > 0"
          type="button"
          class="inline-flex items-center gap-1.5 rounded bg-slate-900 dark:bg-[#007acc] px-3.5 py-1.5 text-xs font-medium text-white hover:bg-slate-800 dark:hover:bg-[#1177bb] transition"
          @click="notifStore.markAllRead()"
        >
          <CheckCheck class="w-3.5 h-3.5" />
          Mark all read
        </button>
      </div>
    </div>

    <!-- Filter Toggle -->
    <div class="flex items-center justify-between border-b border-slate-200 dark:border-[#2d2d2d] pb-3">
      <label class="inline-flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700 dark:text-[#cccccc]">
        <input
          v-model="unreadOnly"
          type="checkbox"
          class="rounded border-slate-300 dark:border-[#3e3e42] text-[#007acc] focus:ring-1 focus:ring-[#007acc] h-3.5 w-3.5 bg-white dark:bg-[#3c3c3c]"
          @change="toggleUnread"
        />
        Show unread only
      </label>

      <span class="text-xs text-slate-500 dark:text-[#989898]">
        {{ notifStore.unreadCount }} unread
      </span>
    </div>

    <!-- Notification List -->
    <div class="space-y-2.5">
      <div
        v-for="notif in notifStore.notifications"
        :key="notif.id"
        :class="[
          'rounded border p-4 transition cursor-pointer',
          !notif.is_read
            ? 'bg-blue-50/30 dark:bg-[#252526] border-blue-300 dark:border-[#007acc]/40 hover:border-blue-400 dark:hover:border-[#007acc]'
            : 'bg-white dark:bg-[#252526] border-slate-200 dark:border-[#2d2d2d] hover:border-slate-300 dark:hover:border-[#3e3e42]'
        ]"
        @click="handleNotificationClick(notif)"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-start gap-3">
            <div
              :class="[
                'p-2 rounded mt-0.5 border',
                notif.notification_type === 'overlap_detected' ? 'bg-[#cca700]/15 text-[#cca700] border-[#cca700]/30' :
                notif.notification_type === 'case_overdue' ? 'bg-[#f48771]/15 text-[#f48771] border-[#f48771]/30' :
                'bg-[#007acc]/15 text-[#4fc1ff] border-[#007acc]/30'
              ]"
            >
              <GitCompare v-if="notif.notification_type === 'overlap_detected'" class="w-4 h-4" />
              <AlertTriangle v-else-if="notif.notification_type === 'case_overdue'" class="w-4 h-4" />
              <Bell v-else class="w-4 h-4" />
            </div>

            <div>
              <div class="flex items-center gap-2">
                <h2 :class="['text-xs font-semibold text-slate-900 dark:text-[#d4d4d4]', !notif.is_read ? 'text-blue-950 dark:text-white' : '']">
                  {{ notif.title }}
                </h2>
                <span v-if="!notif.is_read" class="w-2 h-2 rounded-full bg-[#007acc]"></span>
              </div>
              <p class="text-xs text-slate-600 dark:text-[#cccccc] mt-1 leading-relaxed">
                {{ notif.message }}
              </p>
            </div>
          </div>

          <div class="flex flex-col items-end gap-1.5 flex-shrink-0">
            <span class="text-xs text-slate-400 dark:text-[#989898]">
              {{ notif.created_at?.slice(0, 16).replace('T', ' ') }}
            </span>
            <span class="text-xs font-medium text-blue-600 dark:text-[#4fc1ff] hover:underline inline-flex items-center gap-1">
              View <ArrowRight class="w-3 h-3" />
            </span>
          </div>
        </div>
      </div>

      <div v-if="notifStore.notifications.length === 0 && !notifStore.loading">
        <EmptyState
          title="No notifications"
          description="You have no unread notifications or alerts."
        />
      </div>
    </div>
  </div>
</template>
