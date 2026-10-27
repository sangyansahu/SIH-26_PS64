<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell, ChevronDown, Menu, Search, Shield, LogOut } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import ThemeToggle from '@/components/ThemeToggle.vue'

const emit = defineEmits<{ 'toggle-menu': [] }>()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()
const pageName = computed(() => {
  const path = route.path
  if (path === '/user') return 'My Grievances'
  if (path === '/') return auth.isIndustry ? 'Industry Dashboard' : 'Casework Overview'
  if (path.startsWith('/complaints/')) return 'Case detail'
  if (path === '/complaints') return 'Complaints register'
  if (path.startsWith('/institutions/')) return 'Institution profile'
  if (path === '/institutions') return 'Institution directory'
  if (path === '/overlaps') return 'Overlap review'
  if (path === '/reports') return 'Reports & analytics'
  if (path === '/notifications') return 'Notifications'
  if (path === '/imports') return 'Data imports'
  if (path === '/admin') return 'Administration'
  return 'Workspace'
})

const initials = computed(() => (auth.user?.name || 'Admin').split(/\s+/).map((part) => part[0]).join('').slice(0, 2).toUpperCase())

async function signOut() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="topbar">
    <button class="icon-button mobile-menu" aria-label="Open navigation" @click="emit('toggle-menu')"><Menu :size="20" /></button>
    <div class="breadcrumb"><span>Casework</span><span class="breadcrumb-slash">/</span><strong>{{ pageName }}</strong></div>
    <div class="topbar-tools">
      <label class="global-search">
        <Search :size="17" />
        <input v-model="ui.globalSearch" type="search" placeholder="Search cases or institutions" aria-label="Search cases or institutions" />
        <kbd>⌘ K</kbd>
      </label>
      <ThemeToggle />
      <button v-if="!auth.isUser" class="icon-button topbar-notifications" aria-label="Open notifications" @click="router.push('/notifications')">
        <Bell :size="19" />
        <span v-if="ui.unreadNotifications > 0" class="notification-dot"></span>
      </button>
      <div class="topbar-divider"></div>
      <div class="operator-menu">
        <div class="operator-avatar">{{ initials }}</div>
        <div class="operator-copy">
          <strong>{{ auth.user?.name || 'Authorized User' }}</strong>
          <span>{{ auth.roleDisplay }}</span>
        </div>
        <button class="icon-button operator-menu-button" aria-label="Sign out" title="Sign out" @click="signOut"><LogOut :size="16" /></button>
      </div>

    </div>
  </header>
  <div v-if="ui.isDemoMode" class="demo-strip">
    <span class="demo-strip-mark"></span>
    <span><strong>Demo / fallback records:</strong> one or more API endpoints are unavailable; fictional sample records may be shown.</span>
    <span class="demo-strip-right"><Shield :size="14" /> Not connected to live AICTE systems</span>
  </div>
</template>
