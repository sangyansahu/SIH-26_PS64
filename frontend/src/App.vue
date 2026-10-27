<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const { initTheme } = useTheme()

onMounted(async () => {
  initTheme()
  if (authStore.token) await authStore.fetchMe()
  if (!authStore.isAuthenticated && route.path !== '/login') {
    router.replace({ path: '/login', query: { redirect: route.fullPath } })
  }
})
</script>

<template>
  <router-view />
</template>
