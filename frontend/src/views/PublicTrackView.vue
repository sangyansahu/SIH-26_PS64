<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Search,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Building2,
  Layers,
  AlertCircle,
  FileText,
  Paperclip,
  ArrowRight,
  Info
} from 'lucide-vue-next'
import PublicNav from '@/components/PublicNav.vue'

const route = useRoute()
const router = useRouter()

const searchTicket = ref('')
const loading = ref(false)
const error = ref('')
const complaint = ref<any>(null)

async function fetchComplaint(ticketToLookup: string) {
  const query = ticketToLookup.trim()
  if (!query) {
    error.value = 'Please enter a ticket number to track your grievance.'
    complaint.value = null
    return
  }

  loading.value = true
  error.value = ''
  complaint.value = null

  try {
    const res = await fetch(`http://localhost:5000/api/v1/public/complaints/track/${encodeURIComponent(query)}`)
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'No grievance record found. Please verify the ticket number format.'
    } else {
      complaint.value = data.complaint
      // Update browser URL query without reloading
      router.replace({ query: { ticket: query } })
    }
  } catch (err: any) {
    error.value = 'Unable to connect to the tracking service. Please ensure the backend is reachable.'
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  fetchComplaint(searchTicket.value)
}

function quickFill(ticket: string) {
  searchTicket.value = ticket
  fetchComplaint(ticket)
}

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return 'Pending'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

function getStatusPillClass(status: string): string {
  switch ((status || '').toLowerCase()) {
    case 'disposed':
    case 'resolved':
    case 'closed':
      return 'status-pill-success'
    case 'under review':
      return 'status-pill-info'
    case 'action required':
    case 'escalated':
      return 'status-pill-warning'
    default:
      return 'status-pill-neutral'
  }
}

onMounted(() => {
  const initialTicket = (route.query.ticket as string) || ''
  if (initialTicket) {
    searchTicket.value = initialTicket
    fetchComplaint(initialTicket)
  }
})
</script>

<template>
  <div class="public-layout">
    <PublicNav />

    <main class="public-main">
      <div class="public-container">
        <!-- Page Title -->
        <div class="public-page-header">
          <div class="header-icon-title">
            <Search :size="24" class="header-icon" />
            <h1>Track grievance status</h1>
          </div>
          <p class="public-page-subtitle">
            Enter your AICTE ticket number (e.g. <code>AICTE-2026-XXXXXX</code>) to view status, assigned bureau, and resolution details.
          </p>
        </div>

        <!-- Search Form Card -->
        <div class="track-search-card">
          <form class="track-search-form" @submit.prevent="handleSearch">
            <div class="track-input-wrap">
              <Search :size="18" class="track-search-icon" />
              <input
                v-model="searchTicket"
                type="text"
                placeholder="Enter ticket number (e.g. AICTE-2026-XXXXXX)"
                class="track-input"
                autocomplete="off"
                required
              />
            </div>
            <button
              type="submit"
              class="button button-primary track-btn"
              :disabled="loading"
            >
              <span v-if="loading">Searching…</span>
              <span v-else>Track grievance</span>
            </button>
          </form>

          <div class="track-quick-links">
            <span class="quick-label">Need a reference?</span>
            <span class="quick-help">Check your submission confirmation screen or email acknowledgment.</span>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="public-error-card" role="alert">
          <AlertCircle :size="18" class="error-icon" />
          <div class="error-copy">
            <strong>Grievance not found</strong>
            <p>{{ error }}</p>
          </div>
        </div>

        <!-- Complaint Result Card -->
        <div v-if="complaint" class="track-result-card">
          <!-- Status Header -->
          <div class="result-header">
            <div class="result-ticket-info">
              <h2 class="result-ticket-number">{{ complaint.ticket_number }}</h2>
              <span v-if="complaint.case_number" class="result-case-sub">
                Casework reference: {{ complaint.case_number }}
              </span>
            </div>

            <div class="result-status-badge">
              <span :class="['status-pill', getStatusPillClass(complaint.status)]">
                <CheckCircle2 :size="14" />
                {{ complaint.status }}
              </span>
            </div>
          </div>

          <!-- Progress Stepper -->
          <div class="timeline-stepper">
            <div class="step-item step-completed">
              <div class="step-indicator">
                <CheckCircle2 :size="16" />
              </div>
              <div class="step-content">
                <strong>Lodged</strong>
                <small>{{ formatDate(complaint.received_at) }}</small>
              </div>
            </div>

            <div
              class="step-item"
              :class="{
                'step-completed': complaint.status !== 'Received',
                'step-active': complaint.status === 'Received' || complaint.status === 'Under Review'
              }"
            >
              <div class="step-indicator">
                <Clock :size="16" />
              </div>
              <div class="step-content">
                <strong>Bureau processing</strong>
                <small>{{ complaint.bureau_name || 'Designated bureau' }}</small>
              </div>
            </div>

            <div
              class="step-item"
              :class="{
                'step-completed': complaint.status === 'Disposed' || complaint.status === 'Closed'
              }"
            >
              <div class="step-indicator">
                <ShieldCheck :size="16" />
              </div>
              <div class="step-content">
                <strong>Disposal / closure</strong>
                <small v-if="complaint.disposed_at">{{ formatDate(complaint.disposed_at) }}</small>
                <small v-else>Statutory due: {{ formatDate(complaint.due_at) }}</small>
              </div>
            </div>
          </div>

          <!-- Core Metadata Grid -->
          <div class="result-grid">
            <div class="result-meta-item">
              <span class="meta-label"><Building2 :size="14" /> Concerned institution</span>
              <strong class="meta-value">{{ complaint.institution_name || 'N/A' }}</strong>
              <small class="meta-sub" v-if="complaint.institution_state">
                {{ complaint.institution_state }} · Code: {{ complaint.institution_code || 'Unspecified' }}
              </small>
            </div>

            <div class="result-meta-item">
              <span class="meta-label"><ShieldCheck :size="14" /> Handling bureau</span>
              <strong class="meta-value">{{ complaint.bureau_name }} ({{ complaint.bureau_code }})</strong>
              <small class="meta-sub">Assigned by institutional jurisdiction</small>
            </div>

            <div class="result-meta-item">
              <span class="meta-label"><Layers :size="14" /> Category and priority</span>
              <strong class="meta-value">{{ complaint.category }}</strong>
              <small class="meta-sub">Priority classification: {{ complaint.priority }}</small>
            </div>

            <div class="result-meta-item">
              <span class="meta-label"><Clock :size="14" /> Last action recorded</span>
              <strong class="meta-value">{{ formatDate(complaint.last_action_at) }}</strong>
              <small class="meta-sub">Updated by assigned bureau cell</small>
            </div>
          </div>

          <!-- Grievance Subject & Description -->
          <div class="result-prose-section">
            <h3 class="prose-title"><FileText :size="15" /> Subject</h3>
            <p class="prose-subject">{{ complaint.subject }}</p>

            <h3 class="prose-title prose-title-sub"><FileText :size="15" /> Grievance details</h3>
            <div class="prose-body">{{ complaint.description }}</div>

            <div v-if="complaint.has_supporting_document" class="doc-attachment-badge">
              <Paperclip :size="14" />
              <span>Supporting document attached: <strong>{{ complaint.supporting_document_name || 'Document' }}</strong></span>
            </div>
          </div>

          <!-- Resolution Summary (If available) -->
          <div v-if="complaint.resolution_summary" class="resolution-box">
            <div class="resolution-header">
              <CheckCircle2 :size="16" class="resolution-icon" />
              <strong>Official resolution</strong>
            </div>
            <p class="resolution-body">{{ complaint.resolution_summary }}</p>
            <div class="resolution-footer" v-if="complaint.disposed_at">
              Disposed on: {{ formatDate(complaint.disposed_at) }}
            </div>
          </div>

          <div v-else class="ongoing-notice">
            <Info :size="16" />
            <div>
              <strong>Under review</strong>
              <p>
                The assigned bureau is reviewing this record. Status changes and resolution notes will appear here.
              </p>
            </div>
          </div>

          <!-- Confidentiality Note -->
          <div class="privacy-note">
            <ShieldCheck :size="14" />
            <span>
              Public disclosure: Investigating officer identities, internal notes, and administrative logs remain confidential.
            </span>
          </div>
        </div>
      </div>
    </main>

    <footer class="public-footer">
      <div class="public-container public-footer-inner">
        <span>All India Council for Technical Education · Grievance Redressal Portal</span>
        <span>SIH 2026 Problem Statement 26264</span>
      </div>
    </footer>
  </div>
</template>
