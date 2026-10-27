<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import {
  Bell, LogOut, CheckCircle2, AlertCircle, Info, X, Shield,
  ClipboardList, PlusCircle, Search, Building2, FileSearch, BarChart3,
  Database, Settings2, AlertTriangle, Layers
} from 'lucide-vue-next'
import aicteLogo from '@/assets/aicte-logo.png'
import emblemSvg from '@/assets/emblem-india.svg'

const auth = useAuthStore()
const ui = useUiStore()
const router = useRouter()
const route = useRoute()

const textZoom = ref(100)
function setZoom(level: number) {
  textZoom.value = level
  document.documentElement.style.fontSize = `${(level / 100) * 14}px`
}

async function signOut() {
  await auth.logout()
  router.push('/login')
}

// Current page name for breadcrumb
const pageName = computed(() => {
  const path = route.path
  if (path === '/user') return 'My Grievances'
  if (path === '/register') return 'File Complaint'
  if (path === '/track') return 'Track Complaint'
  if (path === '/') return auth.isSystemAdmin ? 'System Overview' : 'Dashboard'
  if (path.startsWith('/complaints/')) return 'Complaint Details'
  if (path === '/complaints') return 'Complaints'
  if (path.startsWith('/institutions/')) return 'Institution Profile'
  if (path === '/institutions') return 'Institutions'
  if (path === '/overlaps') return 'Overlap Review'
  if (path === '/reports') return 'Reports'
  if (path === '/notifications') return 'Notifications'
  if (path === '/imports') return 'Data Imports'
  if (path === '/admin') return 'Administration'
  return 'Coordination Portal'
})

const initials = computed(() => {
  const name = auth.user?.name || 'User'
  return name.split(/\s+/).map((n) => n[0]).join('').slice(0, 2).toUpperCase()
})

const currentPath = computed(() => route.path)
function isTabActive(path: string): boolean {
  if (path === '/') return currentPath.value === '/'
  return currentPath.value === path || currentPath.value.startsWith(`${path}/`)
}

function openComplainantNotifications() {
  if (route.path !== '/user') {
    router.push('/user').then(() => {
      ui.isComplainantNotifOpen = true
    })
  } else {
    ui.isComplainantNotifOpen = true
  }
}

onMounted(async () => {
  if (auth.isAuthenticated) {
    try {
      const res = await apiClient.get('/notifications')
      const items = res.data.notifications || res.data.items || []
      ui.unreadNotifications = items.filter((n: any) => !n.is_read && !n.read_at).length
    } catch {
      // preview fallback
    }
  }
})
</script>

<template>
  <div class="gigw-portal-container">
    <!-- GIGW Accessibility Top Strip -->
    <div class="gigw-top-strip">
      <div class="gigw-top-inner">
        <div class="gigw-top-left">
          <a href="#main-content" class="gigw-skip-link">Skip to main content</a>
          <span class="gigw-divider">|</span>
          <span class="gigw-govt-title">भारत सरकार | Government of India</span>
        </div>
        <div class="gigw-top-right">
          <span class="gigw-size-label">Text Size:</span>
          <div class="gigw-size-buttons" role="group" aria-label="Font size controls">
            <button
              type="button"
              class="gigw-size-btn"
              :class="{ 'gigw-size-active': textZoom === 90 }"
              title="Decrease Text Size"
              aria-label="Decrease text size"
              @click="setZoom(90)"
            >A-</button>
            <button
              type="button"
              class="gigw-size-btn"
              :class="{ 'gigw-size-active': textZoom === 100 }"
              title="Normal Text Size"
              aria-label="Normal text size"
              @click="setZoom(100)"
            >A</button>
            <button
              type="button"
              class="gigw-size-btn"
              :class="{ 'gigw-size-active': textZoom === 115 }"
              title="Increase Text Size"
              aria-label="Increase text size"
              @click="setZoom(115)"
            >A+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Official Header Banner -->
    <header class="gigw-header-banner">
      <div class="gigw-header-inner">
        <div class="gigw-emblem-lockup">
          <img :src="emblemSvg" alt="State Emblem of India" class="gigw-emblem-img" />
          <div class="gigw-header-text">
            <div class="gigw-council-hindi">अखिल भारतीय तकनीकी शिक्षा परिषद</div>
            <div class="gigw-council-eng">All India Council for Technical Education</div>
            <div class="gigw-subtext">(A Statutory Body Under Ministry of Education, Govt. of India)</div>
          </div>
        </div>

        <div class="gigw-portal-identity">
          <img :src="aicteLogo" alt="AICTE Emblem" class="gigw-aicte-logo" />
          <div class="gigw-portal-titles">
            <span class="gigw-portal-main">Cross-Bureau Complaint Coordination System</span>
            <span class="gigw-portal-tagline">अंतर-ब्यूरो शिकायत समन्वय प्रणाली (SIH 2026 Prototype)</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Tricolour Accent Line -->
    <div class="tricolour-bar">
      <span class="bar-saffron"></span>
      <span class="bar-white"></span>
      <span class="bar-green"></span>
    </div>

    <!-- Government Primary Horizontal Navigation Bar -->
    <nav class="gigw-navbar" aria-label="Main Navigation">
      <div class="gigw-navbar-inner">
        <div class="gigw-nav-links">
          <!-- Public Complainant Navigation -->
          <template v-if="auth.isUser">
            <router-link
              to="/user"
              class="gigw-nav-item"
              :class="{ 'gigw-nav-active': isTabActive('/user') && !ui.isComplainantNotifOpen }"
              @click="ui.isComplainantNotifOpen = false"
            >
              <ClipboardList :size="15" />
              <span>My Grievances</span>
            </router-link>
            <button
              type="button"
              class="gigw-nav-item"
              :class="{ 'gigw-nav-active': ui.isComplainantNotifOpen }"
              title="View Notifications"
              aria-label="View Notifications"
              @click="openComplainantNotifications"
            >
              <Bell :size="15" />
              <span>Notifications</span>
              <span v-if="ui.unreadNotifications > 0" class="gigw-notif-nav-badge">{{ ui.unreadNotifications }}</span>
            </button>
          </template>

          <!-- Bureau Official Navigation -->
          <template v-else-if="auth.isIndustry">
            <router-link to="/" class="gigw-nav-item" :class="{ 'gigw-nav-active': currentPath === '/' }">
              <Layers :size="15" />
              <span>Overview</span>
            </router-link>
            <router-link to="/complaints" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/complaints') }">
              <ClipboardList :size="15" />
              <span>Complaints</span>
            </router-link>
            <router-link to="/overlaps" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/overlaps') }">
              <FileSearch :size="15" />
              <span>Overlap Review</span>
            </router-link>
            <router-link to="/institutions" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/institutions') }">
              <Building2 :size="15" />
              <span>Institutions</span>
            </router-link>
            <router-link to="/reports" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/reports') }">
              <BarChart3 :size="15" />
              <span>Reports</span>
            </router-link>
            <router-link to="/imports" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/imports') }">
              <Database :size="15" />
              <span>Data Imports</span>
            </router-link>
          </template>

          <!-- System Administrator Navigation -->
          <template v-else-if="auth.isSystemAdmin">
            <router-link to="/admin" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/admin') }">
              <Settings2 :size="15" />
              <span>Administration</span>
            </router-link>
            <router-link to="/" class="gigw-nav-item" :class="{ 'gigw-nav-active': currentPath === '/' }">
              <Layers :size="15" />
              <span>Overview</span>
            </router-link>
            <router-link to="/complaints" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/complaints') }">
              <ClipboardList :size="15" />
              <span>Complaints</span>
            </router-link>
            <router-link to="/overlaps" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/overlaps') }">
              <FileSearch :size="15" />
              <span>Overlap Review</span>
            </router-link>
            <router-link to="/institutions" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/institutions') }">
              <Building2 :size="15" />
              <span>Institutions</span>
            </router-link>
            <router-link to="/reports" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/reports') }">
              <BarChart3 :size="15" />
              <span>Reports</span>
            </router-link>
            <router-link to="/imports" class="gigw-nav-item" :class="{ 'gigw-nav-active': isTabActive('/imports') }">
              <Database :size="15" />
              <span>Data Imports</span>
            </router-link>
          </template>
        </div>

        <!-- User Information & Logout -->
        <div class="gigw-nav-user">
          <button
            v-if="!auth.isUser"
            type="button"
            class="gigw-notif-btn"
            title="View Notifications"
            aria-label="View Notifications"
            @click="router.push('/notifications')"
          >
            <Bell :size="17" />
            <span v-if="ui.unreadNotifications > 0" class="gigw-notif-badge">{{ ui.unreadNotifications }}</span>
          </button>

          <div class="gigw-user-badge">
            <div class="gigw-user-avatar">{{ initials }}</div>
            <div class="gigw-user-info">
              <span class="gigw-user-name">{{ auth.user?.name || 'Authorized Official' }}</span>
              <span class="gigw-user-role">
                {{ auth.roleDisplay }}
                <template v-if="auth.user?.bureau_code">({{ auth.user.bureau_code }})</template>
              </span>
            </div>
          </div>

          <button
            type="button"
            class="gigw-logout-btn"
            title="Sign Out"
            aria-label="Sign Out"
            @click="signOut"
          >
            <LogOut :size="15" />
            <span class="hidden sm:inline">Sign Out</span>
          </button>
        </div>
      </div>
    </nav>

    <!-- Breadcrumb Bar -->
    <div class="gigw-breadcrumb-bar">
      <div class="gigw-breadcrumb-inner">
        <span>Home</span>
        <span class="bc-sep">/</span>
        <span class="font-semibold text-[#003366]">{{ pageName }}</span>
      </div>
    </div>

    <!-- Main Content Canvas -->
    <main id="main-content" class="gigw-main-content">
      <router-view />
    </main>

    <!-- Formal GIGW Footer -->
    <footer class="gigw-footer">
      <div class="gigw-footer-top">
        <div class="gigw-footer-links">
          <a href="#">Website Policies</a>
          <span class="footer-sep">|</span>
          <a href="#">Terms of Use</a>
          <span class="footer-sep">|</span>
          <a href="#">Privacy Policy</a>
          <span class="footer-sep">|</span>
          <a href="#">Hyperlinking Policy</a>
          <span class="footer-sep">|</span>
          <a href="#">Copyright Policy</a>
          <span class="footer-sep">|</span>
          <a href="#">Disclaimer</a>
          <span class="footer-sep">|</span>
          <a href="#">Accessibility Statement</a>
        </div>
      </div>
      <div class="gigw-footer-bottom">
        <p class="text-xs text-[#cbd5e1] [text-wrap:pretty]">
          Portal Designed, Developed and Maintained by All India Council for Technical Education (AICTE), Ministry of Education, Government of India.
        </p>
        <p class="text-xs text-[#cbd5e1] mt-1">
          Nelson Mandela Marg, Vasant Kunj, New Delhi-110070 · Smart India Hackathon 2026 Prototype · Last Updated: 27 October 2026
        </p>
      </div>
    </footer>

    <!-- Toast Notification -->
    <Transition name="toast">
      <div
        v-if="ui.toastMessage"
        class="toast-message"
        :class="`toast-${ui.toastKind}`"
        role="status"
        aria-live="polite"
      >
        <CheckCircle2 v-if="ui.toastKind === 'success'" :size="18" />
        <AlertCircle v-else-if="ui.toastKind === 'error'" :size="18" />
        <Info v-else :size="18" />
        <span>{{ ui.toastMessage }}</span>
        <button
          class="icon-button toast-close"
          aria-label="Dismiss notification"
          @click="ui.toastMessage = ''"
        >
          <X :size="15" />
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.gigw-portal-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f4f6f8;
  color: #1b2533;
}

/* Accessibility Top Strip */
.gigw-top-strip {
  background-color: #0b2545;
  color: #ffffff;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px solid #133966;
}
.gigw-top-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.gigw-top-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.gigw-skip-link {
  color: #ffffff;
  text-decoration: underline;
}
.gigw-skip-link:focus {
  outline: 2px solid #ff9933;
  outline-offset: 2px;
}
.gigw-divider {
  color: #4a6488;
}
.gigw-govt-title {
  color: #e2e8f0;
}
.gigw-top-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.gigw-size-label {
  color: #cbd5e1;
}
.gigw-size-buttons {
  display: inline-flex;
  gap: 2px;
}
.gigw-size-btn {
  background: #1b365d;
  color: #ffffff;
  border: 1px solid #3b5984;
  padding: 1px 6px;
  font-size: 12px;
  font-weight: 700;
  border-radius: 2px;
  cursor: pointer;
}
.gigw-size-btn:hover {
  background: #ff9933;
  color: #000000;
}
.gigw-size-active {
  background: #ff9933;
  color: #000000;
  border-color: #ff9933;
}

/* Header Banner */
.gigw-header-banner {
  background: #ffffff;
  border-bottom: 1px solid #dee2e6;
  padding: 10px 0;
}
.gigw-header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.gigw-emblem-lockup {
  display: flex;
  align-items: center;
  gap: 12px;
}
.gigw-emblem-img {
  width: 36px;
  height: 48px;
  object-fit: contain;
}
.gigw-header-text {
  display: flex;
  flex-direction: column;
}
.gigw-council-hindi {
  font-size: 15px;
  font-weight: 700;
  color: #003366;
  line-height: 1.2;
}
.gigw-council-eng {
  font-size: 14px;
  font-weight: 700;
  color: #003366;
  line-height: 1.2;
}
.gigw-subtext {
  font-size: 12px;
  color: #555555;
}
.gigw-portal-identity {
  display: flex;
  align-items: center;
  gap: 12px;
}
.gigw-aicte-logo {
  width: 44px;
  height: 44px;
  object-fit: contain;
}
.gigw-portal-titles {
  display: flex;
  flex-direction: column;
  text-align: right;
}
@media (max-width: 768px) {
  .gigw-portal-titles {
    text-align: left;
  }
}
.gigw-portal-main {
  font-size: 14px;
  font-weight: 700;
  color: #003366;
}
.gigw-portal-tagline {
  font-size: 12px;
  color: #555555;
}

/* Tricolour Accent Line */
.tricolour-bar {
  display: flex;
  height: 4px;
  width: 100%;
}
.bar-saffron {
  flex: 1;
  background-color: #ff9933;
}
.bar-white {
  flex: 1;
  background-color: #ffffff;
}
.bar-green {
  flex: 1;
  background-color: #138808;
}

/* Primary Horizontal Navigation Bar in Navy Blue */
.gigw-navbar {
  background-color: #003366;
  color: #ffffff;
  border-bottom: 2px solid #002244;
}
.gigw-navbar-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  min-height: 46px;
}
.gigw-nav-links {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
}
.gigw-nav-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  text-decoration: none;
  transition: all 0.15s ease;
  border-top: none;
  border-left: none;
  border-right: none;
  border-bottom: 3px solid transparent;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
}
.gigw-nav-item:hover {
  background-color: #0b2545;
  color: #ffffff;
}
.gigw-nav-active {
  background-color: #0b2545;
  color: #ff9933;
  border-bottom: 3px solid #ff9933;
}
.gigw-notif-nav-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1px 6px;
  border-radius: 9999px;
  background-color: #c72e2e;
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
  margin-left: 4px;
}

/* Nav User controls */
.gigw-nav-user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
}
.gigw-notif-btn {
  position: relative;
  background: transparent;
  color: #ffffff;
  border: none;
  padding: 6px;
  cursor: pointer;
  border-radius: 4px;
}
.gigw-notif-btn:hover {
  background-color: #0b2545;
}
.gigw-notif-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: #c72e2e;
  color: #ffffff;
  font-size: 12px;
  font-weight: bold;
  padding: 1px 4px;
  border-radius: 8px;
  min-width: 16px;
  text-align: center;
}
.gigw-user-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  border-left: 1px solid #1a3c66;
  padding-left: 12px;
}
.gigw-user-avatar {
  width: 28px;
  height: 28px;
  background-color: #ff9933;
  color: #000000;
  font-size: 12px;
  font-weight: bold;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.gigw-user-info {
  display: flex;
  flex-direction: column;
}
.gigw-user-name {
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.2;
}
.gigw-user-role {
  font-size: 12px;
  color: #cbd5e1;
}
.gigw-logout-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background-color: #1b365d;
  color: #ffffff;
  border: 1px solid #3b5984;
  padding: 5px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 3px;
  cursor: pointer;
}
.gigw-logout-btn:hover {
  background-color: #c72e2e;
  border-color: #c72e2e;
}

/* Breadcrumb Bar */
.gigw-breadcrumb-bar {
  background-color: #ffffff;
  border-bottom: 1px solid #dee2e6;
  padding: 8px 0;
}
.gigw-breadcrumb-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6c757d;
}
.bc-sep {
  color: #ced4da;
}

.gigw-main-content {
  flex: 1;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 16px;
  box-sizing: border-box;
  min-width: 0;
}

/* Footer */
.gigw-footer {
  background-color: #0b2545;
  color: #e2e8f0;
  border-top: 3px solid #ff9933;
  margin-top: 40px;
}
.gigw-footer-top {
  border-bottom: 1px solid #1a3c66;
  padding: 12px 16px;
}
.gigw-footer-links {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 8px 12px;
  font-size: 12px;
}
.gigw-footer-links a {
  color: #e2e8f0;
  text-decoration: none;
}
.gigw-footer-links a:hover {
  text-decoration: underline;
  color: #ffffff;
}
.footer-sep {
  color: #4a6488;
}
.gigw-footer-bottom {
  max-width: 1280px;
  margin: 0 auto;
  padding: 14px 16px;
  text-align: center;
}
</style>
