<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useComplaintsStore } from '@/stores/complaints'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'
import StatusBadge from '@/components/StatusBadge.vue'
import PriorityBadge from '@/components/PriorityBadge.vue'
import Modal from '@/components/Modal.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { Bureau, Institution } from '@/types'
import {
  Search,
  Filter,
  RotateCcw,
  PlusCircle,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  Clock,
  AlertTriangle,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const store = useComplaintsStore()
const authStore = useAuthStore()

const bureaus = ref<Bureau[]>([])
const institutions = ref<Institution[]>([])
const isNewModalOpen = ref(false)

// New Complaint Form
const form = ref({
  institution_id: '',
  category: 'Fee Overcharging / Capitation',
  subject: '',
  description: '',
  receiving_bureau_id: '',
  priority: 'Medium',
  external_reference: '',
})
const formError = ref<string | null>(null)
const isSubmitting = ref(false)

const categories = ref<string[]>([
  'Fee Overcharging / Capitation',
  'Faculty Quality / Non-Payment',
  'Infrastructure Deficiencies',
  'Ragging Incident',
  'Approval / Accreditation Fraud',
  'Admission Irregularity',
  'General Administration',
])
const statuses = ref<string[]>([
  'Received',
  'Under Review',
  'Action Required',
  'Awaiting Response',
  'Escalated',
  'Disposed',
])
const priorities = ref<string[]>(['Critical', 'High', 'Medium', 'Low'])

async function loadMetadata() {
  try {
    const [bRes, iRes, metaRes] = await Promise.all([
      apiClient.get('/bureaus'),
      apiClient.get('/institutions', { params: { per_page: 100 } }),
      apiClient.get('/complaints/meta').catch(() => ({ data: {} })),
    ])
    bureaus.value = bRes.data.bureaus || []
    institutions.value = iRes.data.items || []

    if (metaRes.data?.categories?.length) {
      categories.value = metaRes.data.categories
    }
    if (metaRes.data?.statuses?.length) {
      statuses.value = metaRes.data.statuses
    }
    if (metaRes.data?.priorities?.length) {
      priorities.value = metaRes.data.priorities
    }

    if (bureaus.value.length > 0 && !form.value.receiving_bureau_id) {
      form.value.receiving_bureau_id = String(authStore.user?.bureau_id || bureaus.value[0].id)
    }
    if (institutions.value.length > 0 && !form.value.institution_id) {
      form.value.institution_id = String(institutions.value[0].id)
    }
  } catch (err) {
    console.error('Metadata load error:', err)
  }
}

function applyQueryParams() {
  if (route.query.action === 'new' && !authStore.isSeniorAuthority) {
    isNewModalOpen.value = true
  }
  if (route.query.is_overdue === 'true') {
    store.isOverdueFilter = true
  } else if (route.query.is_overdue === 'false') {
    store.isOverdueFilter = false
  }
  if (route.query.q || route.query.search) {
    store.search = String(route.query.q || route.query.search)
  }
  if (route.query.bureau) {
    const bCode = String(route.query.bureau).toUpperCase()
    const found = bureaus.value.find((b) => b.code.toUpperCase() === bCode)
    if (found) {
      store.bureauFilter = found.id
    }
  }
  if (route.query.bureau_id) {
    store.bureauFilter = Number(route.query.bureau_id)
  }
  if (route.query.status) {
    store.statusFilter = String(route.query.status)
  }
  if (route.query.priority) {
    store.priorityFilter = String(route.query.priority)
  }
}

onMounted(async () => {
  await loadMetadata()
  applyQueryParams()
  store.fetchComplaints()
})

watch(
  () => route.query,
  () => {
    applyQueryParams()
    store.fetchComplaints()
  }
)

// Debounced search
let searchTimer: any = null
watch(
  () => store.search,
  () => {
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      store.page = 1
      store.fetchComplaints()
    }, 300)
  }
)

async function handleCreateComplaint() {
  if (!form.value.subject || !form.value.description) {
    formError.value = 'Subject and description are required.'
    return
  }
  isSubmitting.value = true
  formError.value = null

  const res = await store.createComplaint({
    ...form.value,
    institution_id: Number(form.value.institution_id),
    receiving_bureau_id: Number(form.value.receiving_bureau_id),
  })

  isSubmitting.value = false
  if (res.success) {
    isNewModalOpen.value = false
    form.value.subject = ''
    form.value.description = ''
    form.value.external_reference = ''
    router.push(`/complaints/${res.complaint.id}`)
  } else {
    formError.value = res.error
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Top Action Bar -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-slate-900 dark:text-[#d4d4d4]">
          Complaints
        </h1>
        <p class="text-xs text-slate-500 dark:text-[#989898] mt-0.5">
          Review grievances, assign bureau ownership, and monitor deadlines
        </p>
      </div>

      <button
        v-if="!authStore.isSeniorAuthority"
        type="button"
        class="inline-flex items-center gap-1.5 rounded bg-slate-900 dark:bg-[#007acc] px-3.5 py-1.5 text-xs font-medium text-white hover:bg-slate-800 dark:hover:bg-[#1177bb] transition"
        @click="isNewModalOpen = true"
      >
        <PlusCircle class="w-3.5 h-3.5" />
        New Complaint
      </button>
    </div>

    <!-- Filter Bar -->
    <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-3.5 space-y-3">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <!-- Search Input -->
        <div class="md:col-span-2 relative">
          <Search class="w-4 h-4 text-slate-400 dark:text-[#989898] absolute left-3 top-2.5 pointer-events-none" />
          <input
            v-model="store.search"
            type="text"
            aria-label="Search complaints"
            placeholder="Search by case number, institution, category, or docket reference..."
            class="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc] placeholder-slate-400 dark:placeholder-[#aaaaaa] transition"
          />
        </div>

        <!-- Bureau Filter -->
        <div>
          <select
            v-model="store.bureauFilter"
            aria-label="Filter by bureau"
            class="w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] transition bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
            @change="store.page = 1; store.fetchComplaints()"
          >
            <option :value="''">All Bureaus and Cells</option>
            <option v-for="b in bureaus" :key="b.id" :value="b.id">
              {{ b.code }}: {{ b.name }}
            </option>
          </select>
        </div>

        <!-- Priority Filter -->
        <div>
          <select
            v-model="store.priorityFilter"
            aria-label="Filter by priority"
            class="w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] transition bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
            @change="store.page = 1; store.fetchComplaints()"
          >
            <option value="">All Priorities</option>
            <option v-for="p in priorities" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
      </div>

      <!-- Secondary Filter Row: Status Pills & Overdue Toggle -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100 dark:border-[#2d2d2d]">
        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-xs font-medium text-slate-400 dark:text-[#989898] mr-1">Status:</span>
          <button
            v-for="st in ['', ...statuses]"
            :key="st"
            type="button"
            :class="[
              'px-2.5 py-1 rounded text-xs font-medium transition',
              store.statusFilter === st
                ? 'bg-slate-900 dark:bg-[#007acc] text-white'
                : 'bg-slate-100 dark:bg-[#2d2d2d] text-slate-600 dark:text-[#cccccc] hover:bg-slate-200 dark:hover:bg-[#37373d] hover:text-slate-900 dark:hover:text-white'
            ]"
            @click="store.statusFilter = st; store.page = 1; store.fetchComplaints()"
          >
            {{ st || 'All' }}
          </button>
        </div>

        <div class="flex items-center gap-3">
          <!-- Overdue toggle -->
          <label class="inline-flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700 dark:text-[#cccccc]">
            <input
              v-model="store.isOverdueFilter"
              type="checkbox"
              class="rounded border-slate-300 dark:border-[#3e3e42] text-[#f48771] focus:ring-1 focus:ring-[#f48771] h-3.5 w-3.5 bg-white dark:bg-[#3c3c3c]"
              @change="store.page = 1; store.fetchComplaints()"
            />
            <span class="flex items-center gap-1 text-red-700 dark:text-[#f48771]">
              <Clock class="w-3.5 h-3.5" />
              Overdue only
            </span>
          </label>

          <button
            type="button"
            class="inline-flex items-center gap-1 text-xs font-medium text-slate-500 dark:text-[#989898] hover:text-slate-800 dark:hover:text-[#cccccc]"
            @click="store.resetFilters()"
          >
            <RotateCcw class="w-3.5 h-3.5" />
            Reset filters
          </button>
        </div>
      </div>
    </div>

    <!-- Case Table -->
    <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-200 dark:border-[#2d2d2d] bg-slate-50 dark:bg-[#1e1e1e] text-xs font-semibold text-slate-600 dark:text-[#cccccc]">
              <th class="py-2.5 px-4">Case #</th>
              <th class="py-2.5 px-4">Institution</th>
              <th class="py-2.5 px-4">Subject & Category</th>
              <th class="py-2.5 px-4">Bureau</th>
              <th class="py-2.5 px-4">Officer</th>
              <th class="py-2.5 px-4">Priority</th>
              <th class="py-2.5 px-4">Status</th>
              <th class="py-2.5 px-4">Due Date</th>
              <th class="py-2.5 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-[#2d2d2d] text-xs">
            <tr
              v-for="c in store.complaints"
              :key="c.id"
              class="hover:bg-slate-50/80 dark:hover:bg-[#2a2d2e] transition"
            >
              <!-- Case Number -->
              <td class="py-3 px-4 font-mono font-medium text-slate-900 dark:text-[#d4d4d4] whitespace-nowrap">
                <router-link
                  :to="`/complaints/${c.id}`"
                  class="text-blue-600 dark:text-[#4fc1ff] hover:underline"
                >
                  {{ c.case_number }}
                </router-link>
                <div v-if="c.external_reference" class="text-xs text-slate-400 dark:text-[#989898] font-sans">
                  Ref: {{ c.external_reference }}
                </div>
              </td>

              <!-- Institution -->
              <td class="py-3 px-4 max-w-[200px]">
                <router-link
                  :to="`/institutions/${c.institution_id}`"
                  class="font-medium text-slate-900 dark:text-[#cccccc] hover:text-blue-600 dark:hover:text-[#4fc1ff] line-clamp-1"
                >
                  {{ c.institution_name }}
                </router-link>
                <div class="text-xs text-slate-400 dark:text-[#989898]">
                  {{ c.institution_code }} · {{ c.institution_state }}
                </div>
              </td>

              <!-- Subject & Category -->
              <td class="py-3 px-4 max-w-xs">
                <p class="font-medium text-slate-800 dark:text-[#cccccc] line-clamp-1" :title="c.subject">
                  {{ c.subject }}
                </p>
                <span class="inline-block mt-0.5 text-xs text-slate-500 dark:text-[#989898]">
                  {{ c.category }}
                </span>
              </td>

              <!-- Bureau -->
              <td class="py-3 px-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 dark:bg-[#2d2d2d] text-slate-700 dark:text-[#cccccc] border border-slate-200 dark:border-[#3e3e42]">
                  {{ c.current_bureau_code }}
                </span>
              </td>

              <!-- Officer -->
              <td class="py-3 px-4 whitespace-nowrap text-slate-600 dark:text-[#989898]">
                {{ c.assigned_officer_name || 'Unassigned' }}
              </td>

              <!-- Priority -->
              <td class="py-3 px-4 whitespace-nowrap">
                <PriorityBadge :priority="c.priority" size="sm" />
              </td>

              <!-- Status -->
              <td class="py-3 px-4 whitespace-nowrap">
                <StatusBadge :status="c.status" size="sm" />
              </td>

              <!-- Due Date -->
              <td class="py-3 px-4 whitespace-nowrap">
                <div class="flex items-center gap-1.5">
                  <span
                    :class="[
                      c.is_overdue
                        ? 'text-red-700 dark:text-[#f48771] font-semibold bg-red-50 dark:bg-[#f48771]/15 px-1.5 py-0.5 rounded border border-red-200 dark:border-[#f48771]/30'
                        : 'text-slate-600 dark:text-[#989898]',
                    ]"
                  >
                    {{ c.due_at ? c.due_at.slice(0, 10) : 'N/A' }}
                  </span>
                  <span
                    v-if="c.is_overdue"
                    class="rounded bg-[#f48771]/20 text-[#f48771] text-xs font-semibold px-1.5 py-0.5"
                  >
                    Overdue
                  </span>
                </div>
              </td>

              <!-- Action Link -->
              <td class="py-3 px-4 text-right whitespace-nowrap">
                <router-link
                  :to="`/complaints/${c.id}`"
                  class="inline-flex items-center gap-1 font-medium text-slate-700 dark:text-[#cccccc] hover:text-slate-900 dark:hover:text-white"
                >
                  View
                  <ArrowRight class="w-3 h-3" />
                </router-link>
              </td>
            </tr>

            <tr v-if="store.complaints.length === 0 && !store.loading">
              <td colspan="9" class="py-12">
                <EmptyState
                  title="No complaints match these filters"
                  description="Try adjusting your keywords, selecting different status filters, or resetting the search options."
                >
                  <template #action>
                    <button
                      type="button"
                      class="px-3 py-1.5 rounded bg-slate-900 dark:bg-[#007acc] text-white text-xs font-medium hover:bg-slate-800 dark:hover:bg-[#1177bb]"
                      @click="store.resetFilters()"
                    >
                      Clear filters
                    </button>
                  </template>
                </EmptyState>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <div class="flex items-center justify-between border-t border-slate-200 dark:border-[#2d2d2d] px-4 py-3 bg-slate-50 dark:bg-[#1e1e1e]">
        <div class="text-xs text-slate-500 dark:text-[#989898]">
          Showing <span class="font-medium text-slate-800 dark:text-[#cccccc]">{{ store.complaints.length }}</span> of <span class="font-medium text-slate-800 dark:text-[#cccccc]">{{ store.total }}</span> complaints
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            :disabled="store.page <= 1"
            class="inline-flex items-center gap-1 rounded border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-2.5 py-1 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-50 dark:hover:bg-[#37373d] disabled:opacity-40 transition"
            @click="store.page--; store.fetchComplaints()"
          >
            <ChevronLeft class="w-3.5 h-3.5" />
            Previous
          </button>

          <span class="text-xs font-medium text-slate-700 dark:text-[#cccccc] px-2">
            Page {{ store.page }} of {{ store.pages }}
          </span>

          <button
            type="button"
            :disabled="store.page >= store.pages"
            class="inline-flex items-center gap-1 rounded border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-2.5 py-1 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-50 dark:hover:bg-[#37373d] disabled:opacity-40 transition"
            @click="store.page++; store.fetchComplaints()"
          >
            Next
            <ChevronRight class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Lodge New Complaint -->
    <Modal
      :is-open="isNewModalOpen"
      title="Register Complaint"
      max-width="xl"
      @close="isNewModalOpen = false"
    >
      <form class="space-y-4" @submit.prevent="handleCreateComplaint">
        <div v-if="formError" class="p-3 rounded bg-red-50 dark:bg-[#f48771]/15 text-xs text-red-700 dark:text-[#f48771] border border-red-200 dark:border-[#f48771]/30">
          {{ formError }}
        </div>

        <div>
          <label for="complaint-institution" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Institution *</label>
          <select
            id="complaint-institution"
            v-model="form.institution_id"
            required
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
          >
            <option v-for="inst in institutions" :key="inst.id" :value="inst.id">
              {{ inst.name }} (ID: {{ inst.institution_code }}) · {{ inst.state }}
            </option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="complaint-bureau" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Receiving bureau *</label>
            <select
              id="complaint-bureau"
              v-model="form.receiving_bureau_id"
              required
              class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
            >
              <option v-for="b in bureaus" :key="b.id" :value="b.id">
                {{ b.code }}: {{ b.name }}
              </option>
            </select>
          </div>

          <div>
            <label for="complaint-priority" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Priority level *</label>
            <select
              id="complaint-priority"
              v-model="form.priority"
              required
              class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
            >
              <option value="Critical">Critical (7-day SLA)</option>
              <option value="High">High (15-day SLA)</option>
              <option value="Medium">Medium (30-day SLA)</option>
              <option value="Low">Low (45-day SLA)</option>
            </select>
          </div>
        </div>

        <div>
          <label for="complaint-category" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Category *</label>
          <select
            id="complaint-category"
            v-model="form.category"
            required
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
          >
            <option v-for="cat in categories" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
        </div>

        <div>
          <label for="complaint-external-ref" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Docket or external reference (optional)</label>
          <input
            id="complaint-external-ref"
            v-model="form.external_reference"
            type="text"
            placeholder="e.g. CPGRAMS docket number, court writ, or FIR reference"
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
          />
        </div>

        <div>
          <label for="complaint-subject" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Subject *</label>
          <input
            id="complaint-subject"
            v-model="form.subject"
            type="text"
            required
            placeholder="Brief summary of the issue"
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
          />
        </div>

        <div>
          <label for="complaint-desc" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Description *</label>
          <textarea
            id="complaint-desc"
            v-model="form.description"
            rows="4"
            required
            placeholder="Details, dates, involved parties, and specific allegations..."
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
          />
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          class="px-3 py-1.5 rounded border border-slate-300 dark:border-[#3e3e42] text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-100 dark:hover:bg-[#37373d]"
          @click="isNewModalOpen = false"
        >
          Cancel
        </button>
        <button
          type="button"
          :disabled="isSubmitting"
          class="px-4 py-1.5 rounded bg-slate-900 dark:bg-[#007acc] text-xs font-medium text-white hover:bg-slate-800 dark:hover:bg-[#1177bb] disabled:opacity-50"
          @click="handleCreateComplaint"
        >
          <span v-if="isSubmitting">Saving complaint...</span>
          <span v-else>Register complaint</span>
        </button>
      </template>
    </Modal>
  </div>
</template>
