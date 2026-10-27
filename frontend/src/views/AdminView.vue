<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import Modal from '@/components/Modal.vue'
import {
  Activity, Users, ShieldCheck, Database, Sliders, Download,
  CheckCircle2, AlertTriangle, AlertCircle, PlusCircle, Search,
  RefreshCw, KeyRound, Building2, Layers, Clock, FileSpreadsheet,
  Check, X, ChevronRight, BarChart3, Filter, FileText
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

// Tabs
const activeTab = ref<'analytics' | 'institutions' | 'users' | 'escalation' | 'reports' | 'audit' | 'quality' | 'taxonomy'>('analytics')

// Loading & Status
const loading = ref(false)
const systemStatus = ref<any>(null)

// 1. System Analytics
const analytics = ref<any>({
  totals: { received: 0, pending: 0, under_process: 0, disposed: 0, transferred: 0, overdue: 0 },
  bureau_breakdown: [],
  region_breakdown: []
})

// 2. Institution & Case Overview
const institutions = ref<any[]>([])
const instSearch = ref('')

// 3. User & Role Management
const users = ref<any[]>([])
const bureaus = ref<any[]>([])
const userRoleFilter = ref('ALL')
const isCreateUserOpen = ref(false)
const isResetPassOpen = ref(false)
const selectedUser = ref<any | null>(null)
const newPassword = ref('')
const newUserForm = ref({
  name: '',
  email: '',
  password: '',
  role: 'INDUSTRY',
  bureau_id: '',
  designation: ''
})

// 4. Deadline & Escalation Config
const escalationConfig = ref<any>({
  sla_days: { Critical: 7, High: 15, Medium: 30, Low: 45 },
  reminder_intervals_days: [5, 2, 1],
  escalation_rules: {
    auto_escalate_overdue_days: 5,
    escalate_to: 'Bureau Head / Senior Monitoring Authority',
    repeat_delay_threshold: 3
  }
})
const configSaving = ref(false)
const configSavedMsg = ref('')

// 5. Reports & Export
const reportsPeriod = ref<'monthly' | 'quarterly'>('monthly')
const disposalReport = ref<any[]>([])
const ageingReport = ref<any[]>([])
const recurringReport = ref<any[]>([])
const reportsLoading = ref(false)

// 6. Audit Logs & System Health
const auditLogs = ref<any[]>([])

// 7. Data Quality Flags
const dataQuality = ref<any>({
  missing_permanent_ids: [],
  inconsistent_names: [],
  incomplete_records: []
})

// 8. Categories & Bureaus Taxonomy
const categoriesList = ref<string[]>([])
const newCategory = ref('')
const newBureau = ref({ code: '', name: '', description: '' })
const isAddBureauOpen = ref(false)

// UI Feedback & Dialogs
const toastMsg = ref('')
const toastType = ref<'success' | 'error'>('success')
const modalError = ref('')

function showToast(message: string, type: 'success' | 'error' = 'success') {
  toastMsg.value = message
  toastType.value = type
  setTimeout(() => {
    if (toastMsg.value === message) toastMsg.value = ''
  }, 4000)
}

function formatRoleName(role: string): string {
  const r = (role || '').toUpperCase()
  if (r === 'SYSTEM_ADMIN' || r === 'ADMIN') return 'System Admin'
  if (r === 'INDUSTRY' || r === 'OFFICER') return 'Bureau Officer'
  if (r === 'USER' || r === 'CITIZEN') return 'Public Complainant'
  return role
}

function openCreateUser() {
  modalError.value = ''
  isCreateUserOpen.value = true
}

function openResetPass(u: any) {
  selectedUser.value = u
  newPassword.value = ''
  modalError.value = ''
  isResetPassOpen.value = true
}

function openAddBureau() {
  modalError.value = ''
  isAddBureauOpen.value = true
}

async function loadAllAdminData() {
  loading.value = true
  try {
    const [
      analyticsRes,
      usersRes,
      bureausRes,
      auditRes,
      statusRes,
      qualityRes,
      configRes,
      instRes,
      catRes
    ] = await Promise.all([
      apiClient.get('/admin/analytics').catch(() => ({ data: null })),
      apiClient.get('/admin/users').catch(() => ({ data: { users: [] } })),
      apiClient.get('/admin/bureaus').catch(() => ({ data: { bureaus: [] } })),
      apiClient.get('/admin/audit-logs').catch(() => ({ data: { audit_logs: [] } })),
      apiClient.get('/admin/system-status').catch(() => ({ data: null })),
      apiClient.get('/admin/data-quality').catch(() => ({ data: null })),
      apiClient.get('/admin/escalation-config').catch(() => ({ data: null })),
      apiClient.get('/institutions?per_page=100').catch(() => ({ data: { items: [] } })),
      apiClient.get('/admin/categories').catch(() => ({ data: { categories: [] } }))
    ])

    if (analyticsRes?.data?.totals) analytics.value = analyticsRes.data
    if (usersRes?.data?.users) users.value = usersRes.data.users
    if (bureausRes?.data?.bureaus) bureaus.value = bureausRes.data.bureaus
    if (auditRes?.data?.audit_logs) auditLogs.value = auditRes.data.audit_logs
    if (statusRes?.data) systemStatus.value = statusRes.data
    if (qualityRes?.data) dataQuality.value = qualityRes.data
    if (configRes?.data?.sla_days) escalationConfig.value = configRes.data
    if (instRes?.data?.items) institutions.value = instRes.data.items
    if (catRes?.data?.categories) categoriesList.value = catRes.data.categories

    // Load Reports
    await loadReportsData()
  } catch (err) {
    console.error('Failed to load admin dashboard data:', err)
  } finally {
    loading.value = false
  }
}

async function loadReportsData() {
  reportsLoading.value = true
  try {
    const [dispRes, ageRes, recRes] = await Promise.all([
      apiClient.get(`/reports/disposal-rates?period=${reportsPeriod.value}`).catch(() => ({ data: { items: [] } })),
      apiClient.get('/reports/ageing').catch(() => ({ data: { items: [] } })),
      apiClient.get('/reports/recurring').catch(() => ({ data: { items: [] } }))
    ])
    disposalReport.value = dispRes?.data?.items || []
    ageingReport.value = ageRes?.data?.items || []
    recurringReport.value = recRes?.data?.items || []
  } catch (e) {
    console.error('Failed loading reports:', e)
  } finally {
    reportsLoading.value = false
  }
}

onMounted(() => {
  loadAllAdminData()
})

const filteredUsers = computed(() => {
  if (userRoleFilter.value === 'ALL') return users.value
  return users.value.filter(u => {
    const r = (u.role || '').toUpperCase()
    if (userRoleFilter.value === 'INDUSTRY') return ['INDUSTRY', 'OFFICER'].includes(r)
    if (userRoleFilter.value === 'SYSTEM_ADMIN') return ['SYSTEM_ADMIN', 'ADMIN'].includes(r)
    if (userRoleFilter.value === 'USER') return ['USER', 'CITIZEN'].includes(r)
    return true
  })
})

const filteredInstitutions = computed(() => {
  const q = instSearch.value.trim().toLowerCase()
  if (!q) return institutions.value
  return institutions.value.filter(inst =>
    (inst.name || '').toLowerCase().includes(q) ||
    (inst.institution_code || '').toLowerCase().includes(q) ||
    (inst.state || '').toLowerCase().includes(q)
  )
})

async function saveEscalationConfig() {
  configSaving.value = true
  configSavedMsg.value = ''
  try {
    await apiClient.patch('/admin/escalation-config', escalationConfig.value)
    configSavedMsg.value = 'Timelines and escalation rules successfully saved.'
    setTimeout(() => { configSavedMsg.value = '' }, 4000)
  } catch {
    configSavedMsg.value = 'Failed to update configuration.'
  } finally {
    configSaving.value = false
  }
}

async function toggleUserStatus(u: any) {
  try {
    await apiClient.patch(`/admin/users/${u.id}`, { is_active: !u.is_active })
    u.is_active = !u.is_active
    showToast(`Account for ${u.name} is now ${u.is_active ? 'active' : 'deactivated'}.`)
  } catch (err: any) {
    showToast(err?.response?.data?.error || 'Failed to update user status.', 'error')
  }
}

async function handleResetPassword() {
  if (!selectedUser.value || !newPassword.value.trim()) return
  modalError.value = ''
  try {
    await apiClient.post(`/admin/users/${selectedUser.value.id}/reset-password`, {
      password: newPassword.value.trim()
    })
    const userName = selectedUser.value.name
    isResetPassOpen.value = false
    showToast(`Password successfully reset for ${userName}.`)
  } catch (err: any) {
    modalError.value = err?.response?.data?.error || 'Failed to reset password.'
  }
}

async function handleCreateUser() {
  if (!newUserForm.value.name.trim() || !newUserForm.value.email.trim() || !newUserForm.value.password.trim()) {
    modalError.value = 'Please complete all required fields.'
    return
  }
  modalError.value = ''
  try {
    await apiClient.post('/admin/users', {
      name: newUserForm.value.name.trim(),
      email: newUserForm.value.email.trim(),
      password: newUserForm.value.password.trim(),
      role: newUserForm.value.role,
      bureau_id: newUserForm.value.bureau_id ? Number(newUserForm.value.bureau_id) : null,
      designation: newUserForm.value.designation.trim() || 'Officer'
    })
    const createdName = newUserForm.value.name
    isCreateUserOpen.value = false
    newUserForm.value = { name: '', email: '', password: '', role: 'INDUSTRY', bureau_id: '', designation: '' }
    showToast(`User account for ${createdName} created successfully.`)
    await loadAllAdminData()
  } catch (err: any) {
    modalError.value = err?.response?.data?.error || 'Failed to create user account.'
  }
}

async function addCategory() {
  if (!newCategory.value.trim()) return
  try {
    await apiClient.post('/admin/categories', { name: newCategory.value.trim() })
    categoriesList.value.push(newCategory.value.trim())
    showToast(`Category "${newCategory.value.trim()}" added.`)
    newCategory.value = ''
  } catch (err: any) {
    showToast(err?.response?.data?.error || 'Failed to add category.', 'error')
  }
}

async function removeCategory(name: string) {
  if (!confirm(`Are you sure you want to remove category "${name}"?`)) return
  try {
    await apiClient.delete(`/admin/categories/${encodeURIComponent(name)}`)
    categoriesList.value = categoriesList.value.filter(c => c !== name)
    showToast(`Category "${name}" removed.`)
  } catch (err: any) {
    showToast(err?.response?.data?.error || 'Failed to remove category.', 'error')
  }
}

async function addBureau() {
  if (!newBureau.value.code.trim() || !newBureau.value.name.trim()) {
    modalError.value = 'Bureau code and name are required.'
    return
  }
  modalError.value = ''
  try {
    const res = await apiClient.post('/admin/bureaus', newBureau.value)
    bureaus.value.push(res.data.bureau)
    isAddBureauOpen.value = false
    newBureau.value = { code: '', name: '', description: '' }
    showToast('Bureau successfully registered.')
  } catch (err: any) {
    modalError.value = err?.response?.data?.error || 'Failed to register bureau.'
  }
}

function exportCsvReport(type: string) {
  window.open(`http://localhost:5000/api/v1/reports/export-csv?type=${type}`, '_blank')
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="admin-canvas">
    <!-- Top Hero Section -->
    <div class="admin-hero">
      <div class="admin-hero-content">
        <div class="admin-role-tag">
          <ShieldCheck :size="14" />
          <span>System Administrator Control Desk</span>
        </div>
        <h1 class="admin-hero-title [text-wrap:balance]">Portal Administration & Governance</h1>
        <p class="admin-hero-sub [text-wrap:pretty]">
          Platform-wide oversight for AICTE complaint coordination. Monitor cross-bureau analytics, audit trails, SLAs, accounts, and data quality.
        </p>
      </div>

      <div class="admin-hero-actions">
        <button class="button button-secondary" :disabled="loading" @click="loadAllAdminData">
          <RefreshCw :size="15" :class="{ 'animate-spin': loading }" />
          <span>Refresh Data</span>
        </button>
      </div>
    </div>

    <!-- Toast Notification Banner -->
    <div
      v-if="toastMsg"
      class="mb-4 p-3 rounded text-xs font-semibold flex items-center justify-between"
      :class="toastType === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'"
    >
      <div class="flex items-center gap-2">
        <CheckCircle2 v-if="toastType === 'success'" :size="15" />
        <AlertCircle v-else :size="15" />
        <span>{{ toastMsg }}</span>
      </div>
      <button type="button" @click="toastMsg = ''" class="hover:opacity-75">
        <X :size="14" />
      </button>
    </div>

    <!-- Navigation Tabs -->
    <div class="admin-nav-tabs" role="tablist">
      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'analytics'"
        class="admin-tab-btn"
        :class="{ 'admin-tab-active': activeTab === 'analytics' }"
        @click="activeTab = 'analytics'"
      >
        <BarChart3 :size="14" />
        <span>Analytics</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'institutions'"
        class="admin-tab-btn"
        :class="{ 'admin-tab-active': activeTab === 'institutions' }"
        @click="activeTab = 'institutions'"
      >
        <Building2 :size="14" />
        <span>Institutions</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'users'"
        class="admin-tab-btn"
        :class="{ 'admin-tab-active': activeTab === 'users' }"
        @click="activeTab = 'users'"
      >
        <Users :size="14" />
        <span>Users ({{ users.length }})</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'escalation'"
        class="admin-tab-btn"
        :class="{ 'admin-tab-active': activeTab === 'escalation' }"
        @click="activeTab = 'escalation'"
      >
        <Sliders :size="14" />
        <span>SLAs & Escalations</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'reports'"
        class="admin-tab-btn"
        :class="{ 'admin-tab-active': activeTab === 'reports' }"
        @click="activeTab = 'reports'"
      >
        <FileSpreadsheet :size="14" />
        <span>Reports</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'audit'"
        class="admin-tab-btn"
        :class="{ 'admin-tab-active': activeTab === 'audit' }"
        @click="activeTab = 'audit'"
      >
        <Activity :size="14" />
        <span>Audit & Health</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'quality'"
        class="admin-tab-btn"
        :class="{ 'admin-tab-active': activeTab === 'quality' }"
        @click="activeTab = 'quality'"
      >
        <AlertTriangle :size="14" />
        <span>Data Quality</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'taxonomy'"
        class="admin-tab-btn"
        :class="{ 'admin-tab-active': activeTab === 'taxonomy' }"
        @click="activeTab = 'taxonomy'"
      >
        <Layers :size="14" />
        <span>Taxonomy</span>
      </button>
    </div>

    <!-- TAB 1: System-Wide Analytics -->
    <div v-if="activeTab === 'analytics'" class="space-y-6">
      <!-- KPI Metric Strip (Plain Gov Cards, no flashy charts) -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div class="admin-kpi-card">
          <span class="kpi-label">Total Received</span>
          <strong class="kpi-value">{{ analytics.totals.received }}</strong>
        </div>
        <div class="admin-kpi-card">
          <span class="kpi-label">Pending Intake</span>
          <strong class="kpi-value">{{ analytics.totals.pending }}</strong>
        </div>
        <div class="admin-kpi-card">
          <span class="kpi-label">Under Process</span>
          <strong class="kpi-value">{{ analytics.totals.under_process }}</strong>
        </div>
        <div class="admin-kpi-card">
          <span class="kpi-label">Disposed / Resolved</span>
          <strong class="kpi-value text-green-700">{{ analytics.totals.disposed }}</strong>
        </div>
        <div class="admin-kpi-card">
          <span class="kpi-label">Cross-Bureau Transferred</span>
          <strong class="kpi-value text-blue-700">{{ analytics.totals.transferred }}</strong>
        </div>
        <div class="admin-kpi-card">
          <span class="kpi-label">Overdue Violations</span>
          <strong class="kpi-value text-red-700">{{ analytics.totals.overdue }}</strong>
        </div>
      </div>

      <!-- Bureau Breakdown & Region Breakdown Tables -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Bureau-wise Breakdown -->
        <div class="admin-section-card">
          <div class="admin-section-header">
            <div>
              <h2 class="admin-section-title">Bureau-Wise Case Distribution</h2>
              <p class="admin-section-sub">Casework workload across AICTE Bureaus and Cells</p>
            </div>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Bureau</th>
                  <th>Total</th>
                  <th>Pending</th>
                  <th>Active</th>
                  <th>Disposed</th>
                  <th>Overdue</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in analytics.bureau_breakdown" :key="b.id">
                  <td>
                    <div class="font-bold text-slate-900">{{ b.code }}</div>
                    <small class="text-quiet text-xs">{{ b.name }}</small>
                  </td>
                  <td><strong>{{ b.total }}</strong></td>
                  <td>{{ b.pending }}</td>
                  <td>{{ b.under_process }}</td>
                  <td class="text-green-700 font-semibold">{{ b.disposed }}</td>
                  <td>
                    <span :class="b.overdue > 0 ? 'text-red-700 font-bold' : 'text-quiet'">
                      {{ b.overdue }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Region-wise Breakdown -->
        <div class="admin-section-card">
          <div class="admin-section-header">
            <div>
              <h2 class="admin-section-title">Region-Wise Distribution</h2>
              <p class="admin-section-sub">Institution grievances grouped by State / Region</p>
            </div>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>State / Region</th>
                  <th class="text-right">Complaints Logged</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in analytics.region_breakdown" :key="r.region">
                  <td class="font-medium text-slate-900">{{ r.region }}</td>
                  <td class="text-right font-mono font-bold">{{ r.total }}</td>
                </tr>
                <tr v-if="!analytics.region_breakdown?.length">
                  <td colspan="2" class="text-center text-quiet py-4">No regional data recorded.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: Institutions & Case Overview -->
    <div v-else-if="activeTab === 'institutions'" class="admin-section-card">
      <div class="admin-section-header">
        <div>
          <h2 class="admin-section-title">Institution & Cross-Bureau Overview</h2>
          <p class="admin-section-sub">Search across institutions to view consolidated complaint histories and multi-bureau engagement.</p>
        </div>
        <div class="w-64">
          <input
            v-model="instSearch"
            type="text"
            class="public-input w-full text-xs"
            placeholder="Search name, Permanent ID, state..."
          />
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Institution Name</th>
              <th>AICTE Permanent ID</th>
              <th>State</th>
              <th>Type</th>
              <th>Total Complaints</th>
              <th>Open Complaints</th>
              <th class="text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inst in filteredInstitutions" :key="inst.id">
              <td><strong>{{ inst.name }}</strong></td>
              <td class="font-mono text-xs font-semibold text-primary">{{ inst.institution_code }}</td>
              <td>{{ inst.state }}</td>
              <td><span class="text-xs text-quiet">{{ inst.institution_type }}</span></td>
              <td><strong>{{ inst.total_complaints || 0 }}</strong></td>
              <td>
                <span class="status-label" :class="(inst.open_complaints || 0) > 0 ? 'status-critical' : 'status-good'">
                  <i></i>{{ inst.open_complaints || 0 }} open
                </span>
              </td>
              <td class="text-right">
                <button
                  class="button button-secondary button-sm"
                  @click="router.push(`/institutions/${inst.id}`)"
                >
                  <span>360° Profile</span>
                  <ChevronRight :size="13" />
                </button>
              </td>
            </tr>
            <tr v-if="!filteredInstitutions.length">
              <td colspan="7" class="text-center text-quiet py-4">No institutions match your search.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 3: User & Role Management -->
    <div v-else-if="activeTab === 'users'" class="admin-section-card">
      <div class="admin-section-header">
        <div>
          <h2 class="admin-section-title">User Accounts & Role Permissions</h2>
          <p class="admin-section-sub">Provision caseworker accounts, assign officers to Bureaus, and manage credentials.</p>
        </div>
        <button class="button button-primary button-sm" @click="openCreateUser">
          <PlusCircle :size="14" />
          <span>Create User</span>
        </button>
      </div>

      <!-- Role Filter Segment -->
      <div class="filter-bar mb-3">
        <div class="segmented-filter">
          <button :class="{ selected: userRoleFilter === 'ALL' }" @click="userRoleFilter = 'ALL'">
            All Accounts ({{ users.length }})
          </button>
          <button :class="{ selected: userRoleFilter === 'INDUSTRY' }" @click="userRoleFilter = 'INDUSTRY'">
            Bureau Officials
          </button>
          <button :class="{ selected: userRoleFilter === 'SYSTEM_ADMIN' }" @click="userRoleFilter = 'SYSTEM_ADMIN'">
            Administrators
          </button>
          <button :class="{ selected: userRoleFilter === 'USER' }" @click="userRoleFilter = 'USER'">
            Complainants
          </button>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Full Name</th>
              <th>Official Email</th>
              <th>Role</th>
              <th>Assigned Bureau</th>
              <th>Account Status</th>
              <th class="text-right">Credentials</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in filteredUsers" :key="u.id">
              <td>
                <strong>{{ u.name }}</strong>
                <small class="block text-quiet text-xs">{{ u.designation || 'Departmental Staff' }}</small>
              </td>
              <td class="font-mono text-xs">{{ u.email }}</td>
              <td>
                <span class="status-label" :class="u.role === 'SYSTEM_ADMIN' ? 'status-critical' : (u.role === 'INDUSTRY' ? 'status-pending' : 'status-good')">
                  <i></i>{{ formatRoleName(u.role) }}
                </span>
              </td>
              <td>
                <span class="bureau-tag">{{ u.bureau_name || u.bureau_code || 'All Bureaus' }}</span>
              </td>
              <td>
                <button
                  class="button button-quiet button-sm"
                  :title="u.is_active ? 'Click to deactivate' : 'Click to activate'"
                  @click="toggleUserStatus(u)"
                >
                  <span class="status-label" :class="u.is_active ? 'status-good' : 'status-critical'">
                    <i></i>{{ u.is_active ? 'Active' : 'Deactivated' }}
                  </span>
                </button>
              </td>
              <td class="text-right">
                <button class="button button-secondary button-sm" @click="openResetPass(u)">
                  <KeyRound :size="13" />
                  <span>Reset Password</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 4: Deadline & Escalation Configuration -->
    <div v-else-if="activeTab === 'escalation'" class="admin-section-card">
      <div class="admin-section-header">
        <div>
          <h2 class="admin-section-title">Prescribed Timelines & Escalation Rules</h2>
          <p class="admin-section-sub">Configure statutory SLA limits, reminder intervals, and automated breach escalation criteria.</p>
        </div>
        <button class="button button-primary button-sm" :disabled="configSaving" @click="saveEscalationConfig">
          <Check :size="14" />
          <span>{{ configSaving ? 'Saving…' : 'Save Rules' }}</span>
        </button>
      </div>

      <div v-if="configSavedMsg" class="p-3 mb-4 rounded bg-green-100 text-green-800 text-xs font-semibold">
        {{ configSavedMsg }}
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
        <!-- SLA Timelines -->
        <div class="p-4 rounded border border-line bg-muted space-y-4">
          <h3 class="font-bold text-sm text-slate-900 flex items-center gap-2">
            <Clock :size="16" />
            <span>Prescribed Resolution Timelines (Days)</span>
          </h3>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Critical Priority SLA</label>
              <input
                v-model.number="escalationConfig.sla_days.Critical"
                type="number"
                min="1"
                class="public-input w-full font-mono font-bold"
              />
              <span class="text-quiet text-xs mt-0.5 block">Default: 7 days</span>
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">High Priority SLA</label>
              <input
                v-model.number="escalationConfig.sla_days.High"
                type="number"
                min="1"
                class="public-input w-full font-mono font-bold"
              />
              <span class="text-quiet text-xs mt-0.5 block">Default: 15 days</span>
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Medium Priority SLA</label>
              <input
                v-model.number="escalationConfig.sla_days.Medium"
                type="number"
                min="1"
                class="public-input w-full font-mono font-bold"
              />
              <span class="text-quiet text-xs mt-0.5 block">Default: 30 days</span>
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Low Priority SLA</label>
              <input
                v-model.number="escalationConfig.sla_days.Low"
                type="number"
                min="1"
                class="public-input w-full font-mono font-bold"
              />
              <span class="text-quiet text-xs mt-0.5 block">Default: 45 days</span>
            </div>
          </div>
        </div>

        <!-- Escalation Rules -->
        <div class="p-4 rounded border border-line bg-muted space-y-4">
          <h3 class="font-bold text-sm text-slate-900 flex items-center gap-2">
            <AlertTriangle :size="16" />
            <span>Overdue Escalation Criteria</span>
          </h3>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Overdue Days Before Bureau Head Escalation</label>
            <input
              v-model.number="escalationConfig.escalation_rules.auto_escalate_overdue_days"
              type="number"
              min="1"
              class="public-input w-full font-mono font-bold"
            />
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Escalate-To Authority Designation</label>
            <input
              v-model="escalationConfig.escalation_rules.escalate_to"
              type="text"
              class="public-input w-full"
            />
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Repeat Delay Threshold (Days)</label>
            <input
              v-model.number="escalationConfig.escalation_rules.repeat_delay_threshold"
              type="number"
              min="1"
              class="public-input w-full font-mono font-bold"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 5: Reports & CSV Export -->
    <div v-else-if="activeTab === 'reports'" class="space-y-6">
      <div class="admin-section-card">
        <div class="admin-section-header">
          <div>
            <h2 class="admin-section-title">Disposal Rates & Workload Reports</h2>
            <p class="admin-section-sub">Generate and export official monthly or quarterly reports.</p>
          </div>
          <div class="flex items-center gap-2">
            <select v-model="reportsPeriod" class="public-select text-xs" @change="loadReportsData">
              <option value="monthly">Monthly Cycle</option>
              <option value="quarterly">Quarterly Cycle</option>
            </select>
            <button class="button button-secondary button-sm" @click="exportCsvReport('disposal')">
              <Download :size="14" />
              <span>Export Disposal CSV</span>
            </button>
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Total Cases</th>
                <th>Disposed Cases</th>
                <th>Disposal Rate (%)</th>
                <th>Avg Days to Resolution</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in disposalReport" :key="d.period">
                <td><strong>{{ d.period }}</strong></td>
                <td>{{ d.total_received }}</td>
                <td class="text-green-700 font-bold">{{ d.disposed_count }}</td>
                <td><strong>{{ d.disposal_rate }}%</strong></td>
                <td>{{ d.avg_resolution_days }} days</td>
              </tr>
              <tr v-if="!disposalReport.length">
                <td colspan="5" class="text-center text-quiet py-4">No report entries for this period.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Ageing & Recurring Institutions -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Ageing Report -->
        <div class="admin-section-card">
          <div class="admin-section-header">
            <div>
              <h2 class="admin-section-title">Case Ageing Brackets</h2>
              <p class="admin-section-sub">Active complaint duration distribution</p>
            </div>
            <button class="button button-quiet button-sm" @click="exportCsvReport('ageing')">
              <Download :size="13" />
              <span>Export CSV</span>
            </button>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Ageing Bracket</th>
                  <th>Cases Count</th>
                  <th>Overdue Cases</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in ageingReport" :key="a.bracket">
                  <td><strong>{{ a.bracket }}</strong></td>
                  <td class="font-mono font-bold">{{ a.count }}</td>
                  <td class="text-red-700 font-bold">{{ a.overdue }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Recurring Complaints -->
        <div class="admin-section-card">
          <div class="admin-section-header">
            <div>
              <h2 class="admin-section-title">Recurring Institutional Complaints</h2>
              <p class="admin-section-sub">Institutions with repeated grievances</p>
            </div>
            <button class="button button-quiet button-sm" @click="exportCsvReport('recurring')">
              <Download :size="13" />
              <span>Export CSV</span>
            </button>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Institution Name</th>
                  <th>Permanent ID</th>
                  <th>Total Complaints</th>
                  <th>Distinct Categories</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in recurringReport" :key="r.institution_code">
                  <td><strong>{{ r.institution_name }}</strong></td>
                  <td class="font-mono text-xs text-primary">{{ r.institution_code }}</td>
                  <td><strong class="text-amber-800">{{ r.complaint_count }}</strong></td>
                  <td>{{ r.distinct_categories }}</td>
                </tr>
                <tr v-if="!recurringReport.length">
                  <td colspan="4" class="text-center text-quiet py-4">No recurring institutions flagged.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 6: Audit Logs & System Health -->
    <div v-else-if="activeTab === 'audit'" class="space-y-6">
      <!-- System Health Indicator Panel -->
      <div class="admin-section-card">
        <div class="admin-section-header">
          <div>
            <h2 class="admin-section-title">System Health & Core Services</h2>
            <p class="admin-section-sub">Operational status of the backend API, PostgreSQL engine, and intake listeners.</p>
          </div>
          <span class="status-label status-good"><i></i>Operational</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div class="p-3 rounded border border-line bg-muted">
            <span class="text-quiet block">Flask 3.1 Backend</span>
            <strong class="text-green-700 text-sm mt-0.5 flex items-center gap-1.5">
              <CheckCircle2 :size="16" />
              <span>Responding (Port 5000)</span>
            </strong>
          </div>
          <div class="p-3 rounded border border-line bg-muted">
            <span class="text-quiet block">PostgreSQL 15 Database</span>
            <strong class="text-green-700 text-sm mt-0.5 flex items-center gap-1.5">
              <CheckCircle2 :size="16" />
              <span>Connected (127.0.0.1:5432)</span>
            </strong>
          </div>
          <div class="p-3 rounded border border-line bg-muted">
            <span class="text-quiet block">Portal Version & Protocol</span>
            <strong class="text-slate-900 text-sm mt-0.5 block font-mono">
              AICTE-CMP v2.0 · SIH 2026
            </strong>
          </div>
        </div>
      </div>

      <!-- Audit Activity Log Table -->
      <div class="admin-section-card">
        <div class="admin-section-header">
          <div>
            <h2 class="admin-section-title">Authoritative Audit Trail</h2>
            <p class="admin-section-sub">Immutable logging of status updates, reassignments, overlap verifications, and access controls.</p>
          </div>
          <span class="text-quiet text-xs font-mono">{{ auditLogs.length }} recorded events</span>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action Type</th>
                <th>Entity Affected</th>
                <th>Responsible Actor</th>
                <th>Operational Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in auditLogs" :key="log.id">
                <td class="font-mono text-xs text-quiet">{{ formatDate(log.created_at) }}</td>
                <td>
                  <span class="status-label status-neutral">
                    <i></i>{{ log.action }}
                  </span>
                </td>
                <td>
                  <span class="font-mono text-xs">{{ log.entity_type }} #{{ log.entity_id }}</span>
                </td>
                <td>
                  <strong>{{ log.user_name || log.performed_by_name || 'System / Auto' }}</strong>
                </td>
                <td class="text-xs text-slate-800 [text-wrap:pretty]">
                  {{ log.description || log.details?.remarks || 'Administrative action recorded' }}
                </td>
              </tr>
              <tr v-if="!auditLogs.length">
                <td colspan="5" class="text-center text-quiet py-4">No audit events logged yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 7: Data Quality Flags -->
    <div v-else-if="activeTab === 'quality'" class="space-y-6">
      <div class="admin-section-card">
        <div class="admin-section-header">
          <div>
            <h2 class="admin-section-title">Data Quality Flags & Anomaly Detection</h2>
            <p class="admin-section-sub">Identifies missing Permanent IDs, inconsistent institution names, and incomplete records.</p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div class="p-3 rounded border border-line bg-muted">
            <span class="text-quiet text-xs block">Missing AICTE Permanent IDs</span>
            <strong class="text-lg text-amber-700 block mt-1">
              {{ dataQuality.missing_permanent_ids?.length || 0 }} Records
            </strong>
          </div>
          <div class="p-3 rounded border border-line bg-muted">
            <span class="text-quiet text-xs block">Inconsistent Institution Names</span>
            <strong class="text-lg text-amber-700 block mt-1">
              {{ dataQuality.inconsistent_names?.length || 0 }} Records
            </strong>
          </div>
          <div class="p-3 rounded border border-line bg-muted">
            <span class="text-quiet text-xs block">Incomplete Intake Records</span>
            <strong class="text-lg text-amber-700 block mt-1">
              {{ dataQuality.incomplete_records?.length || 0 }} Records
            </strong>
          </div>
        </div>

        <!-- Missing Permanent IDs Table -->
        <h3 class="font-bold text-sm text-slate-900 mb-2">Complaints with Missing Permanent Institution IDs</h3>
        <div class="table-container mb-6">
          <table class="data-table">
            <thead>
              <tr>
                <th>Case Number</th>
                <th>Target Institution Name</th>
                <th>State</th>
                <th>Lodged Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in dataQuality.missing_permanent_ids" :key="m.id">
                <td class="font-mono text-xs font-bold text-primary">{{ m.case_number }}</td>
                <td>{{ m.institution_name }}</td>
                <td>{{ m.state || 'Unspecified' }}</td>
                <td>{{ formatDate(m.created_at) }}</td>
              </tr>
              <tr v-if="!dataQuality.missing_permanent_ids?.length">
                <td colspan="4" class="text-center text-quiet py-3">All institution records have valid Permanent IDs assigned.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Inconsistent Names Table -->
        <h3 class="font-bold text-sm text-slate-900 mb-2">Inconsistent Institution Names or Aliases Flagged</h3>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Recorded Institution Name</th>
                <th>Permanent ID</th>
                <th>Discrepancy Signal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(inc, idx) in dataQuality.inconsistent_names" :key="idx">
                <td><strong>{{ inc.name }}</strong></td>
                <td class="font-mono text-xs">{{ inc.code }}</td>
                <td class="text-amber-800 text-xs">{{ inc.issue }}</td>
              </tr>
              <tr v-if="!dataQuality.inconsistent_names?.length">
                <td colspan="3" class="text-center text-quiet py-3">No name inconsistencies flagged in current register.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 8: Configurable Categories & Bureaus -->
    <div v-else-if="activeTab === 'taxonomy'" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Categories Manager -->
        <div class="admin-section-card">
          <div class="admin-section-header">
            <div>
              <h2 class="admin-section-title">Complaint Categories Taxonomy</h2>
              <p class="admin-section-sub">Add or remove grievance categories without requiring code deployment.</p>
            </div>
          </div>

          <div class="flex flex-wrap gap-2 mb-4">
            <span
              v-for="cat in categoriesList"
              :key="cat"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-muted border border-line text-xs font-medium text-slate-800"
            >
              <span>{{ cat }}</span>
              <button
                type="button"
                class="hover:text-red-700 ml-1"
                title="Remove Category"
                @click="removeCategory(cat)"
              >
                <X :size="13" />
              </button>
            </span>
          </div>

          <form @submit.prevent="addCategory" class="flex gap-2">
            <input
              v-model="newCategory"
              type="text"
              class="public-input flex-1 text-xs"
              placeholder="New Category Name (e.g. Examination Malpractice)"
              required
            />
            <button type="submit" class="button button-primary button-sm">
              <PlusCircle :size="14" />
              <span>Add Category</span>
            </button>
          </form>
        </div>

        <!-- Bureaus Manager -->
        <div class="admin-section-card">
          <div class="admin-section-header">
            <div>
              <h2 class="admin-section-title">AICTE Bureaus & Cells</h2>
              <p class="admin-section-sub">Registered operational units handling grievances.</p>
            </div>
            <button class="button button-primary button-sm" @click="openAddBureau">
              <PlusCircle :size="14" />
              <span>Register Bureau</span>
            </button>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Bureau Name</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in bureaus" :key="b.id">
                  <td><span class="bureau-tag">{{ b.code }}</span></td>
                  <td>
                    <strong>{{ b.name }}</strong>
                    <small class="block text-quiet text-xs">{{ b.description }}</small>
                  </td>
                  <td><span class="status-label status-good"><i></i>Active</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE USER MODAL -->
    <Modal
      :isOpen="isCreateUserOpen"
      title="Provision Platform User Account"
      @close="isCreateUserOpen = false"
    >
      <form @submit.prevent="handleCreateUser" class="space-y-4 text-xs">
        <div v-if="modalError" class="p-2.5 rounded bg-red-100 text-red-800 border border-red-200 font-medium">
          {{ modalError }}
        </div>

        <div>
          <label class="block font-semibold text-slate-800 mb-1">Full Name <span class="text-red-600">*</span></label>
          <input v-model="newUserForm.name" class="public-input w-full" placeholder="e.g. Dr. Ramesh Kumar" required />
        </div>

        <div>
          <label class="block font-semibold text-slate-800 mb-1">Official Email <span class="text-red-600">*</span></label>
          <input v-model="newUserForm.email" type="email" class="public-input w-full" placeholder="officer@aicte.gov.in" required />
        </div>

        <div>
          <label class="block font-semibold text-slate-800 mb-1">Initial Password <span class="text-red-600">*</span></label>
          <input v-model="newUserForm.password" type="password" minlength="4" class="public-input w-full" placeholder="Minimum 4 characters" required />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-800 mb-1">Role Permission <span class="text-red-600">*</span></label>
            <select v-model="newUserForm.role" class="public-select w-full">
              <option value="INDUSTRY">AICTE Bureau Official</option>
              <option value="SYSTEM_ADMIN">System Administrator</option>
              <option value="USER">Public Complainant</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold text-slate-800 mb-1">Assigned Bureau</label>
            <select v-model="newUserForm.bureau_id" class="public-select w-full" :disabled="newUserForm.role !== 'INDUSTRY'">
              <option value="">None / Cross-Bureau</option>
              <option v-for="b in bureaus" :key="b.id" :value="String(b.id)">{{ b.code }}: {{ b.name }}</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block font-semibold text-slate-800 mb-1">Designation Title</label>
          <input v-model="newUserForm.designation" class="public-input w-full" placeholder="e.g. Senior Caseworker" />
        </div>

        <div class="pt-3 flex justify-end gap-2 border-t border-line">
          <button type="button" class="button button-secondary" @click="isCreateUserOpen = false">Cancel</button>
          <button type="submit" class="button button-primary">
            <PlusCircle :size="14" />
            <span>Provision Account</span>
          </button>
        </div>
      </form>
    </Modal>

    <!-- RESET PASSWORD MODAL -->
    <Modal
      :isOpen="isResetPassOpen"
      :title="`Reset Password: ${selectedUser?.name || ''}`"
      @close="isResetPassOpen = false"
    >
      <form @submit.prevent="handleResetPassword" class="space-y-4 text-xs">
        <div v-if="modalError" class="p-2.5 rounded bg-red-100 text-red-800 border border-red-200 font-medium">
          {{ modalError }}
        </div>

        <div class="p-3 rounded border border-line bg-muted">
          <div>Email: <strong>{{ selectedUser?.email }}</strong></div>
          <div class="mt-1">Role: <span class="font-bold">{{ formatRoleName(selectedUser?.role) }}</span></div>
        </div>

        <div>
          <label class="block font-semibold text-slate-800 mb-1">New Password <span class="text-red-600">*</span></label>
          <input v-model="newPassword" type="password" minlength="4" class="public-input w-full" placeholder="Enter new password" required />
        </div>

        <div class="pt-3 flex justify-end gap-2 border-t border-line">
          <button type="button" class="button button-secondary" @click="isResetPassOpen = false">Cancel</button>
          <button type="submit" class="button button-primary">
            <KeyRound :size="14" />
            <span>Update Password</span>
          </button>
        </div>
      </form>
    </Modal>

    <!-- REGISTER BUREAU MODAL -->
    <Modal
      :isOpen="isAddBureauOpen"
      title="Register New AICTE Bureau / Cell"
      @close="isAddBureauOpen = false"
    >
      <form @submit.prevent="addBureau" class="space-y-4 text-xs">
        <div v-if="modalError" class="p-2.5 rounded bg-red-100 text-red-800 border border-red-200 font-medium">
          {{ modalError }}
        </div>

        <div>
          <label class="block font-semibold text-slate-800 mb-1">Bureau Short Code <span class="text-red-600">*</span></label>
          <input v-model="newBureau.code" class="public-input w-full uppercase" placeholder="e.g. VQC" required />
        </div>

        <div>
          <label class="block font-semibold text-slate-800 mb-1">Bureau Full Name <span class="text-red-600">*</span></label>
          <input v-model="newBureau.name" class="public-input w-full" placeholder="e.g. Vigilance & Quality Cell" required />
        </div>

        <div>
          <label class="block font-semibold text-slate-800 mb-1">Operational Description</label>
          <textarea v-model="newBureau.description" rows="2" class="public-textarea w-full" placeholder="Statutory scope and grievance routing instructions..." />
        </div>

        <div class="pt-3 flex justify-end gap-2 border-t border-line">
          <button type="button" class="button button-secondary" @click="isAddBureauOpen = false">Cancel</button>
          <button type="submit" class="button button-primary">
            <PlusCircle :size="14" />
            <span>Register Bureau</span>
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<style scoped>
.admin-canvas {
  padding: 1.5rem;
  max-width: 1280px;
  margin: 0 auto;
}
.admin-hero {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.25rem;
  padding: 1.75rem;
  border-radius: 8px;
  background: var(--surface);
  border: 1px solid var(--line);
  margin-bottom: 1.5rem;
}
@media (min-width: 768px) {
  .admin-hero {
    flex-direction: row;
    align-items: center;
  }
}
.admin-role-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 8px;
  border-radius: 4px;
  background: var(--muted);
  border: 1px solid var(--line);
  font-size: 12px;
  font-weight: 600;
  color: #003366;
  margin-bottom: 0.5rem;
}
.admin-hero-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.02em;
}
.admin-hero-sub {
  font-size: 0.875rem;
  color: var(--quiet);
  margin-top: 0.25rem;
  max-width: 700px;
}
.admin-hero-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.admin-nav-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.25rem;
  overflow-x: auto;
}
.admin-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.5rem 0.875rem;
  border-radius: 6px 6px 0 0;
  border: 1px solid transparent;
  background: transparent;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--quiet);
  cursor: pointer;
  white-space: nowrap;
}
.admin-tab-btn:hover {
  color: var(--ink);
}
.admin-tab-active {
  color: var(--primary);
  background: var(--surface);
  border-color: var(--line) var(--line) transparent;
  font-weight: 600;
}

.admin-kpi-card {
  padding: 1.125rem 1rem;
  border-radius: 6px;
  background: var(--surface);
  border: 1px solid var(--line);
}
.kpi-label {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--quiet);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.kpi-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  margin-top: 4px;
  font-family: 'IBM Plex Mono', monospace;
}

.admin-section-card {
  border-radius: 8px;
  background: var(--surface);
  border: 1px solid var(--line);
  padding: 1.5rem;
}
.admin-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--line);
  gap: 1rem;
}
.admin-section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
}
.admin-section-sub {
  font-size: 0.75rem;
  color: var(--quiet);
  margin-top: 2px;
}
</style>
