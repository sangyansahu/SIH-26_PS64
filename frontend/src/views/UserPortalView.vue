<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import Modal from '@/components/Modal.vue'
import {
  PlusCircle, Search, FileText, CheckCircle2, Clock3,
  Building2, AlertTriangle, ShieldCheck, RefreshCw,
  ChevronRight, FileCheck, Printer, Bell, Check,
  Send, Upload, AlertCircle, ArrowRight, X, ExternalLink
} from 'lucide-vue-next'
import aicteLogo from '@/assets/aicte-logo.png'
import emblemSvg from '@/assets/emblem-india.svg'

const auth = useAuthStore()
const ui = useUiStore()
const router = useRouter()

const complaints = ref<any[]>([])
const notifications = ref<any[]>([])
const loading = ref(false)
const selectedComplaint = ref<any | null>(null)
const isDetailOpen = ref(false)
const isAckOpen = ref(false)
const isFileNewOpen = ref(false)
const activeTab = ref<'all' | 'action_required' | 'history'>('all')
const searchQuery = ref('')
const statusFilter = ref('all')

const userFirstName = computed(() => {
  const raw = auth.user?.name || 'Complainant'
  const clean = raw.replace(/\s*\(.*?\)/g, '').trim()
  return clean.split(/\s+/)[0] || 'Complainant'
})

// Additional Information Form
const responseText = ref('')
const responseFile = ref<File | null>(null)
const responseSubmitting = ref(false)
const responseSuccessMsg = ref('')
const responseErrorMsg = ref('')

// File New Form
const newCompInstitutionMode = ref<'search' | 'manual'>('search')
const newCompInstQuery = ref('')
const newCompInstResults = ref<any[]>([])
const newCompSelectedInst = ref<any | null>(null)
const newCompManualName = ref('')
const newCompManualState = ref('')
const newCompCategory = ref('Fee Overcharging / Capitation')
const newCompSubject = ref('')
const newCompDescription = ref('')
const newCompPriority = ref('Medium')
const newCompFile = ref<File | null>(null)
const newCompSubmitting = ref(false)
const newCompError = ref('')

const categories = [
  'Fee Overcharging / Capitation',
  'Faculty Quality / Non-Payment',
  'Infrastructure Deficiencies',
  'Ragging Incident',
  'Approval / Accreditation Fraud',
  'Admission Irregularity',
  'General Administration'
]

async function loadData() {
  loading.value = true
  try {
    const [compRes, notifRes] = await Promise.all([
      apiClient.get('/complaints'),
      apiClient.get('/notifications').catch(() => ({ data: { notifications: [] } }))
    ])
    complaints.value = compRes.data.items || []
    notifications.value = notifRes.data.notifications || notifRes.data.items || []
    ui.unreadNotifications = notifications.value.filter((n: any) => !n.is_read).length
  } catch (err) {
    console.error('Failed to load user complaints:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// Institution search debounce
let searchDebounceTimer: any = null
watch(newCompInstQuery, (q) => {
  clearTimeout(searchDebounceTimer)
  if (!q || q.trim().length < 2) {
    newCompInstResults.value = []
    return
  }
  searchDebounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`http://localhost:5000/api/v1/public/institutions?q=${encodeURIComponent(q.trim())}`)
      if (res.ok) {
        const data = await res.json()
        newCompInstResults.value = data.institutions || []
      }
    } catch {
      // preview fallback
    }
  }, 250)
})

function selectNewInst(inst: any) {
  newCompSelectedInst.value = inst
  newCompInstQuery.value = inst.name
  newCompInstResults.value = []
}

function clearNewInst() {
  newCompSelectedInst.value = null
  newCompInstQuery.value = ''
  newCompInstResults.value = []
}

const actionRequiredCount = computed(() => {
  return complaints.value.filter(c => c.requires_action || (c.status === 'Awaiting Response' && c.query_to_complainant)).length
})

const historyComplaints = computed(() => {
  return complaints.value.filter(c => ['Disposed', 'Closed', 'Resolved'].includes(c.status))
})

const activeComplaints = computed(() => {
  return complaints.value.filter(c => !['Disposed', 'Closed', 'Resolved'].includes(c.status))
})

const filteredComplaints = computed(() => {
  if (activeTab.value === 'action_required') {
    return complaints.value.filter(c => c.requires_action || (c.status === 'Awaiting Response' && c.query_to_complainant))
  }
  if (activeTab.value === 'history') {
    return historyComplaints.value
  }
  return complaints.value
})

const statusOptions = computed(() => {
  const set = new Set<string>()
  filteredComplaints.value.forEach(c => {
    if (c.status) set.add(c.status)
  })
  return Array.from(set)
})

const displayedComplaints = computed(() => {
  let list = filteredComplaints.value
  if (statusFilter.value !== 'all') {
    list = list.filter(c => c.status === statusFilter.value)
  }
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(c => {
      const ticket = (c.ticket_number || c.case_number || '').toLowerCase()
      const subj = (c.subject || '').toLowerCase()
      const inst = (c.institution_name || '').toLowerCase()
      const cat = (c.category || '').toLowerCase()
      const bur = (c.bureau_name || c.bureau_code || '').toLowerCase()
      return ticket.includes(q) || subj.includes(q) || inst.includes(q) || cat.includes(q) || bur.includes(q)
    })
  }
  return list
})

const unreadNotifCount = computed(() => notifications.value.filter(n => !n.is_read).length)

async function markAllNotifsRead() {
  try {
    await apiClient.post('/notifications/read-all').catch(() => {})
  } catch {}
  notifications.value = notifications.value.map(n => ({ ...n, is_read: true, read_at: new Date().toISOString() }))
  ui.unreadNotifications = 0
}

function openDetail(comp: any) {
  selectedComplaint.value = comp
  responseText.value = ''
  responseFile.value = null
  responseSuccessMsg.value = ''
  responseErrorMsg.value = ''
  isDetailOpen.value = true
}

function openAck(comp: any) {
  selectedComplaint.value = comp
  isAckOpen.value = true
}

function printReceipt() {
  window.print()
}

async function submitResponse() {
  if (!selectedComplaint.value) return
  if (!responseText.value.trim()) {
    responseErrorMsg.value = 'Please enter your clarification response.'
    return
  }

  responseSubmitting.value = true
  responseErrorMsg.value = ''
  responseSuccessMsg.value = ''

  try {
    const res = await apiClient.post(`/complaints/${selectedComplaint.value.id}/respond-query`, {
      response: responseText.value.trim(),
      additional_document: responseFile.value ? responseFile.value.name : null
    })

    responseSuccessMsg.value = res.data.message || 'Response successfully submitted to AICTE official.'
    selectedComplaint.value.status = 'Under Review'
    selectedComplaint.value.complainant_response = responseText.value.trim()
    selectedComplaint.value.requires_action = false
    await loadData()
  } catch (err: any) {
    responseErrorMsg.value = err.response?.data?.error || 'Failed to submit response. Please try again.'
  } finally {
    responseSubmitting.value = false
  }
}

async function handleFileNewSubmit() {
  newCompError.value = ''
  if (!newCompSubject.value.trim()) {
    newCompError.value = 'Please enter complaint subject.'
    return
  }
  if (!newCompDescription.value.trim() || newCompDescription.value.trim().length < 15) {
    newCompError.value = 'Please provide detailed complaint description (minimum 15 characters).'
    return
  }
  if (newCompInstitutionMode.value === 'search' && !newCompSelectedInst.value && !newCompInstQuery.value.trim()) {
    newCompError.value = 'Please select or search the target institution.'
    return
  }
  if (newCompInstitutionMode.value === 'manual' && !newCompManualName.value.trim()) {
    newCompError.value = 'Please enter the institution name.'
    return
  }

  newCompSubmitting.value = true

  try {
    const formData = new FormData()
    formData.append('complainant_name', auth.user?.name || 'Citizen Complainant')
    formData.append('complainant_email', auth.user?.email || 'user@aicte.gov.in')
    if (newCompInstitutionMode.value === 'search' && newCompSelectedInst.value) {
      formData.append('institution_id', String(newCompSelectedInst.value.id))
      formData.append('institution_name', newCompSelectedInst.value.name)
    } else if (newCompInstitutionMode.value === 'search' && newCompInstQuery.value.trim()) {
      formData.append('institution_name', newCompInstQuery.value.trim())
    } else {
      formData.append('institution_name', newCompManualName.value.trim())
      if (newCompManualState.value) formData.append('institution_state', newCompManualState.value)
    }
    formData.append('category', newCompCategory.value)
    formData.append('subject', newCompSubject.value.trim())
    formData.append('description', newCompDescription.value.trim())
    formData.append('priority', newCompPriority.value)

    if (newCompFile.value) {
      formData.append('file', newCompFile.value)
    }

    const res = await fetch('http://localhost:5000/api/v1/public/complaints', {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    if (!res.ok) {
      newCompError.value = data.error || 'Failed to register complaint.'
      newCompSubmitting.value = false
      return
    }

    isFileNewOpen.value = false
    // reset form
    newCompSubject.value = ''
    newCompDescription.value = ''
    newCompFile.value = null
    clearNewInst()
    await loadData()
  } catch {
    newCompError.value = 'Connection error. Please try again.'
  } finally {
    newCompSubmitting.value = false
  }
}

async function markNotifRead(id: number) {
  try {
    await apiClient.patch(`/notifications/${id}/read`)
    notifications.value = notifications.value.map(n => n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n)
  } catch {
    // local fallback
    notifications.value = notifications.value.map(n => n.id === id ? { ...n, is_read: true } : n)
  }
  ui.unreadNotifications = notifications.value.filter(n => !n.is_read).length
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function statusDotClass(status: string | undefined): string {
  const s = (status || '').toLowerCase()
  if (['action required', 'critical', 'escalated'].includes(s)) return 'status-critical'
  if (['under review', 'in progress', 'awaiting response'].includes(s)) return 'status-pending'
  if (['disposed', 'resolved', 'closed'].includes(s)) return 'status-good'
  if (['received', 'new'].includes(s)) return 'status-new'
  return 'status-neutral'
}
</script>

<template>
  <div class="user-portal-canvas">
    <!-- Welcome Section -->
    <div class="user-portal-hero">
      <div class="user-hero-content">
        <h1 class="user-hero-title [text-wrap:balance]">Welcome back, {{ userFirstName }}</h1>
        <p class="user-hero-sub [text-wrap:pretty]">
          Centralized AICTE grievance management. File complaints, respond to official queries, monitor statutory updates, and download official receipts.
        </p>
      </div>

      <div class="user-hero-actions">
        <button class="button button-primary user-hero-btn" @click="isFileNewOpen = true">
          <PlusCircle :size="16" />
          <span>File New Complaint</span>
        </button>
        <button class="button button-secondary user-hero-btn" @click="router.push('/track')">
          <Search :size="16" />
          <span>Track Complaint</span>
        </button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="portal-nav-tabs" role="tablist">
      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'all'"
        class="portal-tab-btn"
        :class="{ 'portal-tab-active': activeTab === 'all' }"
        @click="activeTab = 'all'"
      >
        <FileText :size="14" />
        <span>All Complaints ({{ complaints.length }})</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'action_required'"
        class="portal-tab-btn"
        :class="{ 'portal-tab-active': activeTab === 'action_required' }"
        @click="activeTab = 'action_required'"
      >
        <AlertTriangle :size="14" />
        <span>Action Required</span>
        <span v-if="actionRequiredCount > 0" class="tab-badge-alert">{{ actionRequiredCount }}</span>
      </button>

      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'history'"
        class="portal-tab-btn"
        :class="{ 'portal-tab-active': activeTab === 'history' }"
        @click="activeTab = 'history'"
      >
        <CheckCircle2 :size="14" />
        <span>Complaint History & Outcomes ({{ historyComplaints.length }})</span>
      </button>
    </div>

    <!-- Complaints Main Panel -->
    <div class="user-section-card">
      <div class="user-section-header">
        <div>
          <h2 class="user-section-title">My Complaints</h2>
          <p class="user-section-sub">
            Registered grievance cases and real-time statutory review status.
          </p>
        </div>

        <div class="user-section-controls">
          <div class="relative user-search-wrapper">
            <Search :size="14" class="user-search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              class="public-input user-search-input"
              placeholder="Search by ID, subject, institution..."
              aria-label="Search complaints"
            />
          </div>

          <select
            v-if="statusOptions.length > 1"
            v-model="statusFilter"
            class="public-select user-status-filter"
            aria-label="Filter by complaint status"
          >
            <option value="all">All Statuses</option>
            <option v-for="st in statusOptions" :key="st" :value="st">{{ st }}</option>
          </select>

          <button class="button button-secondary button-sm" :disabled="loading" title="Refresh records" @click="loadData">
            <RefreshCw :size="14" :class="{ 'animate-spin': loading }" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading && complaints.length === 0" class="user-loading-box">
        <RefreshCw :size="24" class="animate-spin text-quiet" />
        <p>Loading your complaint records…</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="displayedComplaints.length === 0" class="user-empty-box">
        <FileText :size="40" class="text-quiet mb-3" />
        <h3 v-if="searchQuery || statusFilter !== 'all'">No matching complaints found</h3>
        <h3 v-else-if="activeTab === 'action_required'">No pending official queries</h3>
        <h3 v-else-if="activeTab === 'history'">No disposed cases yet</h3>
        <h3 v-else>No complaints registered yet</h3>
        <p v-if="searchQuery || statusFilter !== 'all'">Try clearing the search or status filter to see other records.</p>
        <p v-else-if="activeTab === 'action_required'">All submitted complaints are proceeding under normal review timelines.</p>
        <p v-else-if="activeTab === 'history'">Resolved decisions and disposal summaries will appear here.</p>
        <p v-else>Submit an institutional grievance with instant AICTE ticket allocation.</p>
        <button
          v-if="searchQuery || statusFilter !== 'all'"
          class="button button-secondary mt-3"
          @click="searchQuery = ''; statusFilter = 'all'"
        >
          Reset filters
        </button>
        <button v-else-if="activeTab === 'all'" class="button button-primary mt-4" @click="isFileNewOpen = true">
          <PlusCircle :size="16" />
          <span>File your first complaint</span>
        </button>
      </div>

      <!-- Complaints Table -->
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-ticket">Ticket ID</th>
              <th class="col-subject">Subject & Target Institution</th>
              <th class="col-category">Category</th>
              <th class="col-bureau">Responsible Bureau</th>
              <th class="col-date">Filing Date</th>
              <th class="col-status">Status</th>
              <th class="col-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="c in displayedComplaints"
              :key="c.id || c.ticket_number"
              class="clickable-row"
              @click="openDetail(c)"
            >
              <td class="col-ticket font-mono text-xs font-semibold text-primary">
                {{ c.ticket_number || c.case_number }}
              </td>
              <td class="col-subject">
                <div class="cell-stack">
                  <span class="subject-text">{{ c.subject }}</span>
                  <span class="institution-text">
                    {{ c.institution_name || 'AICTE Affiliated Institution' }}
                    <span v-if="c.institution_code" class="font-mono text-slate-500">({{ c.institution_code }})</span>
                  </span>
                </div>
              </td>
              <td class="col-category">
                <span class="text-xs text-slate-700 leading-snug">{{ c.category }}</span>
              </td>
              <td class="col-bureau">
                <span class="text-xs font-medium text-slate-800">
                  {{ c.bureau_name || c.bureau_code || 'Central Grievance Redressal' }}
                </span>
              </td>
              <td class="col-date">
                <span class="text-xs text-quiet">{{ formatDate(c.created_at || c.received_at) }}</span>
              </td>
              <td class="col-status">
                <span class="status-label" :class="statusDotClass(c.status)">
                  <i></i>
                  <span>{{ c.status }}</span>
                </span>
                <span v-if="c.requires_action || (c.status === 'Awaiting Response' && c.query_to_complainant)" class="action-tag">
                  Action Required
                </span>
              </td>
              <td class="col-actions text-right" @click.stop>
                <button
                  class="button button-secondary button-sm"
                  title="View complete dossier"
                  @click="openDetail(c)"
                >
                  <span>Details</span>
                  <ChevronRight :size="13" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Complainant Notifications Modal (Accessible from blue navigation bar) -->
    <Modal
      :isOpen="ui.isComplainantNotifOpen"
      title="Official Notifications & Communications"
      @close="ui.isComplainantNotifOpen = false"
    >
      <div class="space-y-4">
        <div class="flex items-center justify-between pb-2 border-b border-line">
          <p class="text-xs text-quiet [text-wrap:pretty]">
            Formal notices regarding complaint acknowledgement, Bureau review, clarification requests, and disposals.
          </p>
          <button
            v-if="unreadNotifCount > 0"
            class="button button-secondary button-sm"
            @click="markAllNotifsRead"
          >
            <Check :size="13" />
            <span>Mark all read</span>
          </button>
        </div>

        <div v-if="notifications.length === 0" class="user-empty-box py-8">
          <Bell :size="36" class="text-quiet mb-2" />
          <h3 class="text-sm font-semibold text-slate-800">No notifications recorded</h3>
          <p class="text-xs text-quiet mt-1">You will receive notices here as your cases progress through official review.</p>
        </div>

        <div v-else class="divide-y divide-line border border-line rounded max-h-[60vh] overflow-y-auto">
          <div
            v-for="n in notifications"
            :key="n.id"
            class="p-4 flex items-start justify-between gap-4 transition-colors"
            :class="{ 'bg-blue-50/50': !n.is_read }"
          >
            <div class="flex items-start gap-3">
              <div class="p-2 rounded bg-muted border border-line text-primary mt-0.5 flex-none">
                <Bell :size="15" />
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <strong class="text-xs sm:text-sm text-slate-900">{{ n.title }}</strong>
                  <span v-if="!n.is_read" class="px-1.5 py-0.5 text-xs bg-primary text-white rounded font-medium">New</span>
                </div>
                <p class="text-xs text-slate-700 mt-1 [text-wrap:pretty]">{{ n.message }}</p>
                <div class="text-xs text-quiet mt-1.5 flex items-center gap-2">
                  <span>{{ formatDateTime(n.created_at) }}</span>
                  <span v-if="n.related_complaint_id" class="text-primary font-medium">
                    Ref Case #{{ n.related_complaint_id }}
                  </span>
                </div>
              </div>
            </div>
            <button
              v-if="!n.is_read"
              class="button button-quiet button-sm flex-none"
              title="Mark as read"
              @click="markNotifRead(n.id)"
            >
              <Check :size="13" />
              <span>Mark read</span>
            </button>
          </div>
        </div>

        <div class="pt-3 flex justify-end border-t border-line">
          <button class="button button-secondary button-sm" @click="ui.isComplainantNotifOpen = false">
            Close
          </button>
        </div>
      </div>
    </Modal>

    <!-- Complaint Detail & Respond Query Modal -->
    <Modal
      :isOpen="isDetailOpen"
      :title="`Grievance Dossier: ${selectedComplaint?.ticket_number || selectedComplaint?.case_number || ''}`"
      @close="isDetailOpen = false"
    >
      <div v-if="selectedComplaint" class="space-y-5">
        <!-- Top Status Banner -->
        <div class="p-4 rounded border border-line bg-muted flex items-center justify-between">
          <div>
            <span class="text-xs text-quiet uppercase tracking-wider font-semibold block">Official Status</span>
            <span class="status-label mt-1 text-sm font-semibold" :class="statusDotClass(selectedComplaint.status)">
              <i></i>
              <span>{{ selectedComplaint.status }}</span>
            </span>
          </div>
          <div class="text-right">
            <span class="text-xs text-quiet block">Handling Department / Bureau</span>
            <span class="text-xs font-mono font-medium text-slate-800 mt-1 block">
              {{ selectedComplaint.bureau_name || selectedComplaint.bureau_code || 'Central Grievance Redressal' }}
            </span>
          </div>
        </div>

        <!-- ADDITIONAL INFORMATION REQUEST BOX (Active Clarification Form) -->
        <div
          v-if="selectedComplaint.query_to_complainant || selectedComplaint.status === 'Awaiting Response'"
          class="p-4 rounded border border-amber-300 bg-amber-50"
        >
          <div class="flex items-center gap-2 text-amber-900 font-semibold text-xs mb-2">
            <AlertTriangle :size="16" class="text-amber-700" />
            <span>Official Query from AICTE Reviewer</span>
          </div>
          <div class="p-3 bg-white border border-amber-200 rounded text-xs text-slate-800 [text-wrap:pretty]">
            {{ selectedComplaint.query_to_complainant || 'Additional documentation or clarification is requested for verification.' }}
          </div>

          <!-- Existing Complainant Response if already submitted -->
          <div v-if="selectedComplaint.complainant_response" class="mt-3 p-3 bg-emerald-50 border border-emerald-200 rounded text-xs">
            <div class="font-semibold text-emerald-900 mb-1 flex items-center gap-1.5">
              <CheckCircle2 :size="14" class="text-emerald-600" />
              <span>Your Clarification Response Submitted</span>
            </div>
            <p class="text-emerald-950">{{ selectedComplaint.complainant_response }}</p>
            <div v-if="selectedComplaint.additional_documents" class="mt-1 text-xs text-emerald-800">
              Attached document: <strong>{{ selectedComplaint.additional_documents }}</strong>
            </div>
          </div>

          <!-- Response Form if pending response -->
          <form v-else @submit.prevent="submitResponse" class="mt-3 space-y-3">
            <div>
              <label for="complainant-reply" class="block text-xs font-semibold text-slate-800 mb-1">
                Your Response / Clarification <span class="text-red-600">*</span>
              </label>
              <textarea
                id="complainant-reply"
                v-model="responseText"
                rows="3"
                class="public-textarea w-full text-xs"
                placeholder="Provide the requested details, clarification on fee payments, dates, or missing context..."
                required
              />
            </div>

            <div>
              <label for="response-doc" class="block text-xs font-semibold text-slate-800 mb-1">
                Upload Missing / Supporting Document (Optional)
              </label>
              <input
                id="response-doc"
                type="file"
                class="text-xs"
                @change="e => { const t = e.target as HTMLInputElement; if (t.files) responseFile = t.files[0] }"
              />
            </div>

            <div v-if="responseErrorMsg" class="p-2 bg-red-100 text-red-700 text-xs rounded">
              {{ responseErrorMsg }}
            </div>
            <div v-if="responseSuccessMsg" class="p-2 bg-green-100 text-green-700 text-xs rounded">
              {{ responseSuccessMsg }}
            </div>

            <button
              type="submit"
              class="button button-primary button-sm"
              :disabled="responseSubmitting"
            >
              <Send :size="14" />
              <span>{{ responseSubmitting ? 'Submitting…' : 'Submit Response to Official' }}</span>
            </button>
          </form>
        </div>

        <!-- Official Resolution Decision if Disposed -->
        <div v-if="selectedComplaint.resolution_summary" class="p-4 rounded border border-emerald-500/30 bg-emerald-50">
          <div class="flex items-center gap-2 text-emerald-900 font-semibold text-xs mb-1">
            <CheckCircle2 :size="16" class="text-emerald-600" />
            <span>Official Resolution Decision</span>
          </div>
          <p class="text-sm text-emerald-950 [text-wrap:pretty]">
            {{ selectedComplaint.resolution_summary }}
          </p>
        </div>

        <!-- Key Information Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div class="p-3 rounded border border-line bg-muted">
            <span class="text-quiet block">Target Institution</span>
            <strong class="text-slate-900 text-sm mt-0.5 block">
              {{ selectedComplaint.institution_name || 'AICTE Institution' }}
            </strong>
            <span v-if="selectedComplaint.institution_code" class="font-mono text-slate-600 block mt-0.5">
              Permanent ID: {{ selectedComplaint.institution_code }}
            </span>
            <span v-if="selectedComplaint.institution_state" class="text-quiet mt-0.5 block">
              State: {{ selectedComplaint.institution_state }}
            </span>
          </div>
          <div class="p-3 rounded border border-line bg-muted">
            <span class="text-quiet block">Category & Priority</span>
            <strong class="text-slate-900 text-sm mt-0.5 block">
              {{ selectedComplaint.category }}
            </strong>
            <span class="text-quiet mt-0.5 block">
              Statutory Urgency: {{ selectedComplaint.priority || 'Medium' }}
            </span>
          </div>
        </div>

        <!-- Description -->
        <div>
          <h4 class="text-xs font-semibold uppercase tracking-wider text-quiet mb-1.5">Grievance Particulars</h4>
          <div class="p-3.5 rounded border border-line bg-muted text-xs leading-relaxed text-slate-800 [text-wrap:pretty]">
            <strong class="block text-sm mb-1 text-slate-900">{{ selectedComplaint.subject }}</strong>
            <p>{{ selectedComplaint.description }}</p>
          </div>
        </div>

        <!-- Supporting Document Link if available -->
        <div v-if="selectedComplaint.supporting_document_name" class="p-3 rounded border border-line bg-muted flex items-center justify-between text-xs">
          <div class="flex items-center gap-2">
            <FileCheck :size="16" class="text-primary" />
            <span>Supporting Document: <strong>{{ selectedComplaint.supporting_document_name }}</strong></span>
          </div>
        </div>

        <!-- Milestone Updates Timeline -->
        <div v-if="selectedComplaint.updates && selectedComplaint.updates.length > 0">
          <h4 class="text-xs font-semibold uppercase tracking-wider text-quiet mb-2">Statutory Progress Updates</h4>
          <div class="divide-y divide-line border border-line rounded bg-muted">
            <div v-for="(u, idx) in selectedComplaint.updates" :key="idx" class="p-3 text-xs flex items-start gap-3">
              <Clock3 :size="15" class="text-quiet mt-0.5 flex-none" />
              <div class="flex-1">
                <div class="flex items-center justify-between">
                  <strong class="text-slate-900">{{ u.status }}</strong>
                  <span class="text-quiet">{{ formatDate(u.date) }}</span>
                </div>
                <p class="text-quiet mt-0.5">{{ u.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Actions -->
        <div class="pt-2 flex items-center justify-between border-t border-line">
          <button class="button button-secondary button-sm" @click="openAck(selectedComplaint)">
            <Printer :size="14" />
            <span>Print Official Receipt</span>
          </button>
          <button class="button button-secondary" @click="isDetailOpen = false">Close</button>
        </div>
      </div>
    </Modal>

    <!-- OFFICIAL ACKNOWLEDGEMENT & STATUS SUMMARY RECEIPT MODAL -->
    <Modal
      :isOpen="isAckOpen"
      title="Official Grievance Acknowledgement & Progress Dossier"
      @close="isAckOpen = false"
    >
      <div v-if="selectedComplaint" class="ack-receipt-container">
        <!-- Printable Receipt Box -->
        <div id="printable-receipt" class="ack-printable-box">
          <!-- Official Letterhead -->
          <div class="ack-header">
            <img :src="emblemSvg" alt="Emblem of India" class="ack-emblem" />
            <div class="ack-header-center">
              <h2>अखिल भारतीय तकनीकी शिक्षा परिषद</h2>
              <h3>ALL INDIA COUNCIL FOR TECHNICAL EDUCATION</h3>
              <p>Nelson Mandela Marg, Vasant Kunj, New Delhi - 110070</p>
              <div class="ack-sub-bar">CENTRAL GRIEVANCE MONITORING & REDRESSAL SYSTEM</div>
            </div>
            <img :src="aicteLogo" alt="AICTE Logo" class="ack-aicte-logo" />
          </div>

          <div class="ack-divider"></div>

          <!-- Receipt Identification -->
          <div class="ack-id-row">
            <div>
              <span class="ack-label">GRIEVANCE TICKET NUMBER</span>
              <strong class="ack-ticket font-mono">{{ selectedComplaint.ticket_number || selectedComplaint.case_number }}</strong>
            </div>
            <div class="text-right">
              <span class="ack-label">LODGEMENT DATE</span>
              <strong>{{ formatDate(selectedComplaint.created_at || selectedComplaint.received_at) }}</strong>
            </div>
          </div>

          <!-- Institution & Details Grid -->
          <table class="ack-details-table">
            <tbody>
              <tr>
                <td class="ack-field-title">Complainant:</td>
                <td>{{ auth.user?.name || selectedComplaint.complainant_name || 'Verified Citizen' }}</td>
                <td class="ack-field-title">Official Contact:</td>
                <td>{{ auth.user?.email || selectedComplaint.complainant_email || 'On Record' }}</td>
              </tr>
              <tr>
                <td class="ack-field-title">Target Institution:</td>
                <td><strong>{{ selectedComplaint.institution_name }}</strong></td>
                <td class="ack-field-title">AICTE Permanent ID:</td>
                <td><span class="font-mono font-bold">{{ selectedComplaint.institution_code || '1-XXXXXXXX' }}</span></td>
              </tr>
              <tr>
                <td class="ack-field-title">Grievance Category:</td>
                <td>{{ selectedComplaint.category }}</td>
                <td class="ack-field-title">Allocated Bureau:</td>
                <td>{{ selectedComplaint.bureau_name || selectedComplaint.bureau_code || 'PGRC' }}</td>
              </tr>
              <tr>
                <td class="ack-field-title">Subject Summary:</td>
                <td colspan="3"><strong>{{ selectedComplaint.subject }}</strong></td>
              </tr>
              <tr>
                <td class="ack-field-title">Current Status:</td>
                <td colspan="3">
                  <span class="font-bold uppercase tracking-wider text-primary">{{ selectedComplaint.status }}</span>
                  <span v-if="selectedComplaint.disposed_at" class="text-xs text-quiet ml-2">
                    (Disposed on {{ formatDate(selectedComplaint.disposed_at) }})
                  </span>
                </td>
              </tr>
              <tr v-if="selectedComplaint.resolution_summary">
                <td class="ack-field-title">Official Decision:</td>
                <td colspan="3" class="text-xs leading-relaxed text-slate-800">
                  {{ selectedComplaint.resolution_summary }}
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Statutory Notice -->
          <div class="ack-notice">
            <p>
              * This is a computer-generated statutory acknowledgement generated under the AICTE Cross-Bureau Complaint Coordination Protocol. Please quote the Ticket Number in all future correspondence.
            </p>
          </div>
        </div>

        <div class="pt-4 flex items-center justify-between border-t border-line mt-4">
          <button class="button button-primary" @click="printReceipt">
            <Printer :size="15" />
            <span>Print / Save as PDF</span>
          </button>
          <button class="button button-secondary" @click="isAckOpen = false">Close</button>
        </div>
      </div>
    </Modal>

    <!-- LODGE NEW COMPLAINT MODAL -->
    <Modal
      :isOpen="isFileNewOpen"
      title="File a New Grievance"
      @close="isFileNewOpen = false"
    >
      <form @submit.prevent="handleFileNewSubmit" class="space-y-4 text-xs">
        <!-- Target Institution -->
        <div>
          <label class="block font-semibold text-slate-800 mb-1">
            Target AICTE Institution <span class="text-red-600">*</span>
          </label>
          <div class="flex gap-2 mb-2">
            <button
              type="button"
              class="px-2.5 py-1 rounded border text-xs font-medium"
              :class="newCompInstitutionMode === 'search' ? 'bg-primary text-white border-primary' : 'bg-muted border-line text-slate-700'"
              @click="newCompInstitutionMode = 'search'"
            >
              Search Directory
            </button>
            <button
              type="button"
              class="px-2.5 py-1 rounded border text-xs font-medium"
              :class="newCompInstitutionMode === 'manual' ? 'bg-primary text-white border-primary' : 'bg-muted border-line text-slate-700'"
              @click="newCompInstitutionMode = 'manual'"
            >
              Enter Manually
            </button>
          </div>

          <div v-if="newCompInstitutionMode === 'search'" class="relative">
            <input
              v-model="newCompInstQuery"
              type="text"
              class="public-input w-full"
              placeholder="Type institution name or AICTE Permanent ID (e.g. 1-4123891)..."
              :disabled="Boolean(newCompSelectedInst)"
            />
            <button
              v-if="newCompSelectedInst"
              type="button"
              class="button button-quiet button-sm mt-1"
              @click="clearNewInst"
            >
              <X :size="12" /> Change Selection
            </button>

            <!-- Autocomplete list -->
            <ul
              v-if="!newCompSelectedInst && newCompInstResults.length > 0"
              class="absolute z-20 top-full left-0 right-0 bg-white border border-line rounded shadow-lg max-h-48 overflow-y-auto mt-1"
            >
              <li
                v-for="inst in newCompInstResults"
                :key="inst.id"
                class="p-2.5 hover:bg-muted cursor-pointer border-b border-line last:border-b-0"
                @click="selectNewInst(inst)"
              >
                <div class="font-semibold text-slate-900">{{ inst.name }}</div>
                <div class="text-quiet text-xs">Permanent ID: {{ inst.institution_code }} · {{ inst.state }}</div>
              </li>
            </ul>
          </div>

          <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <input
              v-model="newCompManualName"
              type="text"
              class="public-input"
              placeholder="Institution Name"
            />
            <input
              v-model="newCompManualState"
              type="text"
              class="public-input"
              placeholder="State / Region"
            />
          </div>
        </div>

        <!-- Category & Priority -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label for="modal-cat" class="block font-semibold text-slate-800 mb-1">
              Category <span class="text-red-600">*</span>
            </label>
            <select id="modal-cat" v-model="newCompCategory" class="public-select w-full">
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          <div>
            <label for="modal-prio" class="block font-semibold text-slate-800 mb-1">Urgency Level</label>
            <select id="modal-prio" v-model="newCompPriority" class="public-select w-full">
              <option value="Low">Low - Informational</option>
              <option value="Medium">Medium - Standard inquiry</option>
              <option value="High">High - Time-sensitive</option>
              <option value="Critical">Critical - Urgent / Ragging</option>
            </select>
          </div>
        </div>

        <!-- Subject -->
        <div>
          <label for="modal-subj" class="block font-semibold text-slate-800 mb-1">
            Subject Summary <span class="text-red-600">*</span>
          </label>
          <input
            id="modal-subj"
            v-model="newCompSubject"
            type="text"
            class="public-input w-full"
            placeholder="Brief summary of the grievance"
            required
          />
        </div>

        <!-- Description -->
        <div>
          <label for="modal-desc" class="block font-semibold text-slate-800 mb-1">
            Detailed Description <span class="text-red-600">*</span>
          </label>
          <textarea
            id="modal-desc"
            v-model="newCompDescription"
            rows="4"
            class="public-textarea w-full"
            placeholder="State all relevant facts, dates, academic terms, fee amounts..."
            required
          />
        </div>

        <!-- Supporting Document -->
        <div>
          <label for="modal-file" class="block font-semibold text-slate-800 mb-1">
            Supporting Document (PDF, Word, or image up to 16MB)
          </label>
          <input
            id="modal-file"
            type="file"
            class="text-xs"
            @change="e => { const t = e.target as HTMLInputElement; if (t.files) newCompFile = t.files[0] }"
          />
        </div>

        <div v-if="newCompError" class="p-2.5 bg-red-100 text-red-800 rounded text-xs">
          {{ newCompError }}
        </div>

        <div class="pt-3 flex justify-end gap-2 border-t border-line">
          <button type="button" class="button button-secondary" @click="isFileNewOpen = false">Cancel</button>
          <button type="submit" class="button button-primary" :disabled="newCompSubmitting">
            <PlusCircle :size="15" />
            <span>{{ newCompSubmitting ? 'Registering…' : 'Submit Grievance' }}</span>
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<style scoped>
.user-portal-canvas {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-width: 0;
}
.user-portal-hero {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: 6px;
  background: var(--surface);
  border: 1px solid var(--line);
  margin-bottom: 1.25rem;
  box-sizing: border-box;
}
@media (min-width: 768px) {
  .user-portal-hero {
    flex-direction: row;
    align-items: center;
  }
}
.user-hero-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.01em;
}
.user-hero-sub {
  font-size: 0.8125rem;
  color: var(--quiet);
  margin-top: 0.25rem;
  max-width: 650px;
}
.user-hero-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.user-hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.portal-nav-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.25rem;
  overflow-x: auto;
}
.portal-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.5rem 1rem;
  border-radius: 6px 6px 0 0;
  border: 1px solid transparent;
  background: transparent;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--quiet);
  cursor: pointer;
  white-space: nowrap;
}
.portal-tab-btn:hover {
  color: var(--ink);
}
.portal-tab-active {
  color: var(--primary);
  background: var(--surface);
  border-color: var(--line) var(--line) transparent;
  font-weight: 600;
}
.tab-badge-alert {
  padding: 1px 6px;
  border-radius: 10px;
  background: #c72e2e;
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
}
.action-tag {
  display: inline-block;
  margin-top: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  color: #b45309;
  background: #fef3c7;
  padding: 2px 6px;
  border-radius: 4px;
}

.user-section-card {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-width: 0;
  border-radius: 6px;
  background: var(--surface);
  border: 1px solid var(--line);
  padding: 1.25rem 1.5rem;
  overflow: hidden;
}
.user-section-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--line);
}
@media (min-width: 768px) {
  .user-section-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}
.user-section-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.user-search-wrapper {
  min-width: 200px;
}
.user-search-icon {
  position: absolute;
  left: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--quiet);
  pointer-events: none;
}
.user-search-input {
  padding-left: 2rem;
  padding-top: 0.375rem;
  padding-bottom: 0.375rem;
  font-size: 0.75rem;
  width: 100%;
}
.user-status-filter {
  padding-top: 0.375rem;
  padding-bottom: 0.375rem;
  font-size: 0.75rem;
}
.user-section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
}
.user-section-sub {
  font-size: 0.75rem;
  color: var(--quiet);
  margin-top: 2px;
}

.table-container {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-width: 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.table-container .data-table {
  width: 100%;
  min-width: 700px;
  border-collapse: separate;
  border-spacing: 0;
  box-sizing: border-box;
}
.table-container .data-table thead th {
  padding: 10px 12px;
  background: #f8fafc;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
  border-bottom: 1px solid var(--line);
  box-sizing: border-box;
  white-space: nowrap;
}
.table-container .data-table tbody td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--line);
  font-size: 12px;
  vertical-align: middle;
  box-sizing: border-box;
}
.col-ticket {
  width: 130px;
  white-space: nowrap !important;
}
.col-subject {
  min-width: 200px;
  max-width: 300px;
}
.col-category {
  min-width: 140px;
  max-width: 180px;
}
.col-bureau {
  min-width: 130px;
}
.col-date {
  width: 105px;
  white-space: nowrap !important;
}
.col-status {
  width: 130px;
  white-space: nowrap !important;
}
.col-actions {
  width: 90px;
  text-align: right;
  white-space: nowrap !important;
}
.subject-text {
  display: block;
  font-weight: 500;
  color: #0f172a;
  line-height: 1.35;
  text-wrap: pretty;
}
.institution-text {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
  line-height: 1.25;
}
.user-loading-box, .user-empty-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  text-align: center;
}
.user-empty-box h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
}
.user-empty-box p {
  font-size: 0.875rem;
  color: var(--quiet);
  margin-top: 4px;
}

/* Acknowledgement Box Styles */
.ack-printable-box {
  padding: 1.5rem;
  background: #fff;
  border: 2px solid #003366;
  border-radius: 6px;
  color: #1a202c;
  font-family: inherit;
}
.ack-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  text-align: center;
}
.ack-emblem {
  height: 60px;
  width: auto;
}
.ack-aicte-logo {
  height: 60px;
  width: auto;
}
.ack-header-center h2 {
  font-size: 1rem;
  font-weight: 700;
  color: #003366;
  margin: 0;
}
.ack-header-center h3 {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1a202c;
  margin: 2px 0;
}
.ack-header-center p {
  font-size: 0.7rem;
  color: #4a5568;
  margin: 0;
}
.ack-sub-bar {
  margin-top: 6px;
  padding: 2px 8px;
  background: #003366;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  border-radius: 2px;
}
.ack-divider {
  height: 2px;
  background: linear-gradient(90deg, #ff9933 33%, #ffffff 33%, #ffffff 66%, #138808 66%);
  margin: 1rem 0;
  border-top: 1px solid #cbd5e1;
  border-bottom: 1px solid #cbd5e1;
}
.ack-id-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #cbd5e1;
  margin-bottom: 0.75rem;
}
.ack-label {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  color: #718096;
}
.ack-ticket {
  font-size: 1.1rem;
  color: #003366;
}
.ack-details-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
}
.ack-details-table td {
  padding: 0.4rem 0.5rem;
  border: 1px solid #e2e8f0;
}
.ack-field-title {
  width: 25%;
  background: #f8fafc;
  font-weight: 600;
  color: #4a5568;
}
.ack-notice {
  margin-top: 1rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e2e8f0;
  font-size: 0.65rem;
  color: #718096;
  font-style: italic;
}

@media print {
  body * {
    visibility: hidden;
  }
  #printable-receipt, #printable-receipt * {
    visibility: visible;
  }
  #printable-receipt {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    border: none;
  }
}
</style>
