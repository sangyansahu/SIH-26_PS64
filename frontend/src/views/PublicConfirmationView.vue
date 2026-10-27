<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  CheckCircle2,
  Copy,
  Check,
  Search,
  FilePlus2,
  Printer,
  ShieldCheck,
  Building2,
  Clock,
  Layers,
  FileText
} from 'lucide-vue-next'
import PublicNav from '@/components/PublicNav.vue'

const route = useRoute()
const router = useRouter()

const ticketNumber = computed(() => {
  return (route.query.ticket as string) || (history.state?.ticket_number as string) || 'AICTE-2026-DEMO01'
})

const subject = computed(() => {
  return (route.query.subject as string) || (history.state?.subject as string) || 'Grievance submission acknowledged'
})

const institutionName = computed(() => {
  return (route.query.institution as string) || (history.state?.institution_name as string) || 'Designated Technical Institution'
})

const category = computed(() => {
  return (route.query.category as string) || (history.state?.category as string) || 'General Administration'
})

const bureauName = computed(() => {
  return (route.query.bureau as string) || (history.state?.bureau_name as string) || 'Public Grievance Redressal Cell'
})

const copied = ref(false)

async function copyTicket() {
  try {
    await navigator.clipboard.writeText(ticketNumber.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2400)
  } catch (err) {
    copied.value = true
  }
}

function handlePrint() {
  window.print()
}

function goToTrack() {
  router.push({ path: '/track', query: { ticket: ticketNumber.value } })
}

function goToRegister() {
  router.push('/register')
}
</script>

<template>
  <div class="public-layout">
    <PublicNav />

    <main class="public-main">
      <div class="public-container">
        <!-- Success Banner Card -->
        <div class="confirmation-card">
          <div class="confirmation-badge-row">
            <div class="confirmation-icon-wrap">
              <CheckCircle2 :size="28" />
            </div>
            <div class="confirmation-heading">
              <h1>Grievance registered</h1>
              <p>Your complaint has been recorded in the AICTE case register.</p>
            </div>
          </div>

          <!-- Highlight Ticket Box -->
          <div class="ticket-callout">
            <div class="ticket-callout-top">
              <span class="ticket-label">TICKET NUMBER</span>
            </div>

            <div class="ticket-value-row">
              <code class="ticket-code">{{ ticketNumber }}</code>
              <button
                type="button"
                class="button button-quiet ticket-copy-btn"
                @click="copyTicket"
                :title="copied ? 'Copied to clipboard' : 'Copy ticket number'"
              >
                <Check v-if="copied" :size="15" />
                <Copy v-else :size="15" />
                <span>{{ copied ? 'Copied' : 'Copy Ticket' }}</span>
              </button>
            </div>

            <p class="ticket-instruction">
              Save this ticket number to track progress, bureau responses, and final resolution.
            </p>
          </div>

          <!-- Details Table -->
          <div class="confirmation-details">
            <h2 class="confirmation-section-title">Submission summary</h2>
            <div class="summary-grid">
              <div class="summary-item">
                <span class="summary-label"><Building2 :size="14" /> Institution</span>
                <strong class="summary-value">{{ institutionName }}</strong>
              </div>

              <div class="summary-item">
                <span class="summary-label"><Layers :size="14" /> Category</span>
                <span class="summary-value">{{ category }}</span>
              </div>

              <div class="summary-item">
                <span class="summary-label"><ShieldCheck :size="14" /> Assigned Bureau</span>
                <span class="summary-value">{{ bureauName }}</span>
              </div>

              <div class="summary-item">
                <span class="summary-label"><FileText :size="14" /> Subject</span>
                <span class="summary-value">{{ subject }}</span>
              </div>
            </div>
          </div>

          <!-- Next Steps Guidance -->
          <div class="guidance-box">
            <h3 class="guidance-title"><Clock :size="15" /> Next steps</h3>
            <ol class="guidance-list">
              <li>
                <strong>Bureau intake:</strong> The designated AICTE bureau reviews jurisdiction and determines required actions.
              </li>
              <li>
                <strong>Inter-bureau check:</strong> Related complaints concerning the same institution are cross-referenced.
              </li>
              <li>
                <strong>Resolution:</strong> Directives and closure notes will appear on your tracking page.
              </li>
            </ol>
          </div>

          <!-- Action Buttons -->
          <div class="confirmation-actions">
            <button type="button" class="button button-primary" @click="goToTrack">
              <Search :size="15" />
              <span>Track grievance</span>
            </button>

            <button type="button" class="button button-quiet" @click="handlePrint">
              <Printer :size="15" />
              <span>Print acknowledgment</span>
            </button>

            <button type="button" class="button button-quiet" @click="goToRegister">
              <FilePlus2 :size="15" />
              <span>Register another grievance</span>
            </button>
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
