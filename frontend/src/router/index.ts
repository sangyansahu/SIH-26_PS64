import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'
import AdminView from '@/views/AdminView.vue'
import WorkspaceView from '@/views/WorkspaceView.vue'
import UserPortalView from '@/views/UserPortalView.vue'
import LoginView from '@/views/LoginView.vue'
import PublicRegisterView from '@/views/PublicRegisterView.vue'
import PublicTrackView from '@/views/PublicTrackView.vue'
import PublicConfirmationView from '@/views/PublicConfirmationView.vue'

const routes: RouteRecordRaw[] = [
  { path: '/landing', redirect: '/register' },
  { path: '/register', name: 'public-register', component: PublicRegisterView, meta: { public: true } },
  { path: '/track', name: 'public-track', component: PublicTrackView, meta: { public: true } },
  { path: '/confirmation', name: 'public-confirmation', component: PublicConfirmationView, meta: { public: true } },
  { path: '/login', name: 'login', component: LoginView, meta: { guestOnly: true } },
  {
    path: '/', component: AppLayout, meta: { requiresAuth: true }, children: [
      { path: '', name: 'dashboard', component: WorkspaceView, meta: { requiresRole: 'INDUSTRY' } },
      { path: 'user', name: 'user-portal', component: UserPortalView },
      { path: 'complaints', name: 'complaints', component: WorkspaceView, meta: { requiresRole: 'INDUSTRY' } },
      { path: 'complaints/:id', name: 'complaint-detail', component: WorkspaceView, meta: { requiresRole: 'INDUSTRY' } },
      { path: 'institutions', name: 'institutions', component: WorkspaceView, meta: { requiresRole: 'INDUSTRY' } },
      { path: 'institutions/:id', name: 'institution-profile', component: WorkspaceView, meta: { requiresRole: 'INDUSTRY' } },
      { path: 'overlaps', name: 'overlaps', component: WorkspaceView, meta: { requiresRole: 'INDUSTRY' } },
      { path: 'reports', name: 'reports', component: WorkspaceView, meta: { requiresRole: 'INDUSTRY' } },
      { path: 'notifications', name: 'notifications', component: WorkspaceView, meta: { requiresRole: 'INDUSTRY' } },
      { path: 'imports', name: 'imports', component: WorkspaceView, meta: { requiresRole: 'INDUSTRY' } },
      { path: 'admin', name: 'admin', component: AdminView, meta: { requiresRole: 'SYSTEM_ADMIN' } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()

  // Public pages are always accessible
  if (to.meta.public) {
    return true
  }

  // Authentication check
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // Guest-only (Login page) redirects based on role
  if (to.meta.guestOnly && auth.isAuthenticated) {
    if (auth.isUser) return '/user'
    if (auth.isSystemAdmin) return '/admin'
    return '/'
  }

  // Complainant / USER role isolation:
  // Public complainants can ONLY access /user and public routes
  if (auth.isUser) {
    if (to.path !== '/user' && !to.meta.public) {
      return '/user'
    }
    return true
  }

  // INDUSTRY role restriction:
  // Cannot access System Administration
  if (auth.isIndustry) {
    if (to.meta.requiresRole === 'SYSTEM_ADMIN' || to.path === '/admin') {
      return '/'
    }
  }

  // SYSTEM_ADMIN has access to everything
  return true
})

export default router
