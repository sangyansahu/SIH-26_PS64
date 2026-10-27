<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, LockKeyhole, User as UserIcon, Shield, FileText, Search } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import aicteLogo from '@/assets/aicte-logo.png'
import emblemSvg from '@/assets/emblem-india.svg'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const email = ref('admin')
const password = ref('admin')

const textZoom = ref(100)
function setZoom(level: number) {
  textZoom.value = level
  document.documentElement.style.fontSize = `${(level / 100) * 14}px`
}

async function handleLogin() {
  const ok = await auth.login(email.value, password.value)
  if (ok) {
    if (auth.isUser) {
      router.replace('/user')
    } else if (auth.isSystemAdmin) {
      const destination = typeof route.query.redirect === 'string' && route.query.redirect !== '/' ? route.query.redirect : '/admin'
      router.replace(destination)
    } else {
      const destination = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
      router.replace(destination)
    }
  }
}

function fillRole(roleName: string) {
  if (roleName === 'admin') {
    email.value = 'admin'
    password.value = 'admin'
  } else if (roleName === 'officer') {
    email.value = 'industry'
    password.value = 'industry'
  } else if (roleName === 'user') {
    email.value = 'user'
    password.value = 'user'
  }
}
</script>

<template>
  <div class="gigw-page-wrapper">
    <!-- GIGW Slim Top Accessibility Bar -->
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

    <!-- Main Content Area -->
    <main id="main-content" class="gigw-main-login">
      <div class="gigw-login-card">
        <div class="gigw-card-header">
          <div class="flex items-center gap-2 justify-center mb-1 text-[#003366]">
            <Shield :size="20" />
            <h1 class="text-base font-bold tracking-tight text-[#003366] [text-wrap:balance]">Authorized Portal Login</h1>
          </div>
          <p class="text-xs text-gray-600 text-center [text-wrap:pretty]">
            Sign in with your designated role credentials to access the Cross-Bureau Complaint Coordination System.
          </p>
        </div>

        <div v-if="auth.error" class="login-alert-error" role="alert">
          {{ auth.error }}
        </div>

        <!-- Form -->
        <form class="gigw-login-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label class="form-label" for="login-email">User ID / Official Email <span class="text-red-600">*</span></label>
            <div class="input-with-icon">
              <UserIcon :size="16" class="field-icon" />
              <input
                id="login-email"
                v-model="email"
                type="text"
                class="gov-input"
                required
                autocomplete="username"
                placeholder="Enter User ID or official email"
              />
            </div>
          </div>

          <div class="form-group mt-4">
            <label class="form-label" for="login-password">Password <span class="text-red-600">*</span></label>
            <div class="input-with-icon">
              <LockKeyhole :size="16" class="field-icon" />
              <input
                id="login-password"
                v-model="password"
                type="password"
                class="gov-input"
                required
                autocomplete="current-password"
                placeholder="Enter password"
              />
            </div>
          </div>

          <button
            type="submit"
            class="gov-btn-primary mt-5"
            :disabled="auth.loading"
          >
            <span>{{ auth.loading ? 'Verifying Credentials…' : 'Sign In to Portal' }}</span>
            <ArrowRight :size="15" />
          </button>
        </form>

        <!-- Role Quick-Fill Buttons -->
        <div class="quick-fill-block">
          <span class="quick-fill-label">Select Demo Login Role:</span>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 mt-2">
            <button
              type="button"
              class="quick-fill-btn"
              :class="{ 'quick-fill-btn-selected': email === 'user' }"
              @click="fillRole('user')"
            >
              <div class="font-semibold text-xs text-[#003366]">1. Public User</div>
              <div class="text-xs text-slate-600">Complainant</div>
            </button>

            <button
              type="button"
              class="quick-fill-btn"
              :class="{ 'quick-fill-btn-selected': email === 'industry' }"
              @click="fillRole('officer')"
            >
              <div class="font-semibold text-xs text-[#003366]">2. Bureau Official</div>
              <div class="text-xs text-slate-600">PGRC / AB / RPC</div>
            </button>

            <button
              type="button"
              class="quick-fill-btn"
              :class="{ 'quick-fill-btn-selected': email === 'admin' }"
              @click="fillRole('admin')"
            >
              <div class="font-semibold text-xs text-[#003366]">3. System Admin</div>
              <div class="text-xs text-slate-600">Platform Admin</div>
            </button>
          </div>
        </div>

        <!-- Citizen Grievance Portal Links -->
        <div class="citizen-actions-box">
          <div class="flex items-center justify-between text-xs gap-3">
            <router-link to="/register" class="gov-text-link flex items-center gap-1.5">
              <FileText :size="14" />
              <span>Register New Grievance</span>
            </router-link>
            <span class="text-gray-300">|</span>
            <router-link to="/track" class="gov-text-link flex items-center gap-1.5">
              <Search :size="14" />
              <span>Track Ticket Status</span>
            </router-link>
          </div>
        </div>
      </div>
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
  </div>
</template>

<style scoped>
.gigw-page-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f4f6f8;
  color: #1b2533;
}

/* GIGW Top Accessibility Strip */
.gigw-top-strip {
  background-color: #0b2545;
  color: #ffffff;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px solid #133966;
}
.gigw-top-inner {
  max-width: 1200px;
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
  padding: 12px 0;
}
.gigw-header-inner {
  max-width: 1200px;
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

/* Main Login Box */
.gigw-main-login {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 16px;
}
.gigw-login-card {
  width: 100%;
  max-width: 460px;
  background: #ffffff;
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 24px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}
.gigw-card-header {
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 14px;
  margin-bottom: 18px;
}
.login-alert-error {
  background-color: #fde8e8;
  color: #c72e2e;
  border: 1px solid #f8b4b4;
  padding: 8px 12px;
  font-size: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-label {
  font-size: 12px;
  font-weight: 600;
  color: #212529;
}
.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}
.field-icon {
  position: absolute;
  left: 10px;
  color: #6c757d;
  pointer-events: none;
}
.gov-input {
  width: 100%;
  padding: 8px 12px 8px 34px;
  font-size: 13px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: #ffffff;
  color: #212529;
}
.gov-input:focus {
  border-color: #003366;
  outline: 2px solid rgba(0, 51, 102, 0.25);
}
.gov-btn-primary {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: #003366;
  color: #ffffff;
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.gov-btn-primary:hover:not(:disabled) {
  background-color: #002244;
}
.gov-btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Quick Fill Buttons */
.quick-fill-block {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}
.quick-fill-label {
  font-size: 12px;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.quick-fill-btn {
  background: #f8f9fa;
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 8px 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.15s ease;
}
.quick-fill-btn:hover {
  background: #e9ecef;
  border-color: #003366;
}
.quick-fill-btn-selected {
  background: #e7f1ff;
  border-color: #003366;
  box-shadow: 0 0 0 1px #003366;
}

/* Citizen actions */
.citizen-actions-box {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #e9ecef;
}
.gov-text-link {
  color: #003366;
  font-weight: 500;
  text-decoration: underline;
}
.gov-text-link:hover {
  color: #002244;
}

/* GIGW Footer */
.gigw-footer {
  background-color: #0b2545;
  color: #e2e8f0;
  border-top: 3px solid #ff9933;
}
.gigw-footer-top {
  border-bottom: 1px solid #1a3c66;
  padding: 12px 16px;
}
.gigw-footer-links {
  max-width: 1200px;
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 14px 16px;
  text-align: center;
}
</style>
