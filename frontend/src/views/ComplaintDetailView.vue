<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useComplaintsStore } from '@/stores/complaints'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'
import StatusBadge from '@/components/StatusBadge.vue'
import PriorityBadge from '@/components/PriorityBadge.vue'
import Modal from '@/components/Modal.vue'
import type { Complaint, Bureau, User } from '@/types'
import {
  ArrowLeft,
  Building,
  Calendar,
  Clock,
  UserCheck,
  Send,
  GitCompare,
  FileCheck2,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const store = useComplaintsStore()
const authStore = useAuthStore()

const complaintId = computed(() => Number(route.params.id))
const activeTab = ref<'overview' | 'timeline' | 'overlaps'>('overview')

const bureaus = ref<Bureau[]>([])
const bureauOfficers = ref<User[]>([])

// Modals state
const isStatusModalOpen = ref(false)
const isAssignModalOpen = ref(false)
const isTransferModalOpen = ref(false)

const newStatus = ref('Under Review')
const statusRemarks = ref('')

const selectedOfficerId = ref<number | ''>('')
const assignRemarks = ref('')

const selectedTargetBureauId = ref<number | ''>('')
const transferRemarks = ref('')

const actionError = ref<string | null>(null)
const isActionLoading = ref(false)

const canEdit = computed(() => {
  if (authStore.isAdmin) return true
  if (authStore.isSeniorAuthority) return false
  if (authStore.isOfficer && store.currentComplaint) {
    return store.currentComplaint.current_bureau_id === authStore.user?.bureau_id
  }
  return false
})

async function loadComplaint() {
  await store.fetchComplaintDetail(complaintId.value)
  if (store.currentComplaint) {
    newStatus.value = store.currentComplaint.status
    selectedOfficerId.value = store.currentComplaint.assigned_user_id || ''
  }
}

async function loadBureaus() {
  try {
    const res = await apiClient.get('/bureaus')
    bureaus.value = res.data.bureaus || []
  } catch (err) {
    // Ignore
  }
}

async function loadOfficersForCurrentBureau() {
  if (!store.currentComplaint?.current_bureau_id) return
  try {
    const res = await apiClient.get(`/bureaus/${store.currentComplaint.current_bureau_id}/officers`)
    bureauOfficers.value = res.data.officers || []
  } catch (err) {
    // Ignore
  }
}

onMounted(async () => {
  await loadComplaint()
  await loadBureaus()
  await loadOfficersForCurrentBureau()
})

async function handleUpdateStatus() {
  if (!newStatus.value) return
  isActionLoading.value = true
  actionError.value = null

  const res = await store.updateStatus(complaintId.value, newStatus.value, statusRemarks.value)
  isActionLoading.value = false

  if (res.success) {
    isStatusModalOpen.value = false
    statusRemarks.value = ''
  } else {
    actionError.value = res.error
  }
}

async function handleAssignOfficer() {
  if (!selectedOfficerId.value) return
  isActionLoading.value = true
  actionError.value = null

  const res = await store.assignOfficer(complaintId.value, Number(selectedOfficerId.value), assignRemarks.value)
  isActionLoading.value = false

  if (res.success) {
    isAssignModalOpen.value = false
    assignRemarks.value = ''
  } else {
    actionError.value = res.error
  }
}

async function handleTransferBureau() {
  if (!selectedTargetBureauId.value) return
  isActionLoading.value = true
  actionError.value = null

  const res = await store.transferBureau(complaintId.value, Number(selectedTargetBureauId.value), transferRemarks.value)
  isActionLoading.value = false

  if (res.success) {
    isTransferModalOpen.value = false
    transferRemarks.value = ''
    await loadOfficersForCurrentBureau()
  } else {
    actionError.value = res.error
  }
}
</script>

<template>
  <div v-if="store.currentComplaint" class="space-y-6">
    <!-- Breadcrumbs (Mockup Style) -->
    <div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-[#989898] font-medium">
      <router-link to="/" class="hover:text-blue-600 dark:hover:text-[#38bdf8] transition-colors">Dashboard</router-link>
      <span class="text-slate-400">/</span>
      <router-link to="/complaints" class="hover:text-blue-600 dark:hover:text-[#38bdf8] transition-colors">Complaints</router-link>
      <span class="text-slate-400">/</span>
      <span class="text-slate-900 dark:text-white font-mono font-semibold">{{ store.currentComplaint.case_number }}</span>
    </div>

    <!-- Header Section -->
    <div>
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div class="flex flex-wrap items-center gap-2.5">
            <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-white font-mono">
              {{ store.currentComplaint.case_number }}
            </h1>
            <span class="rounded-lg bg-blue-50 dark:bg-[#142e4e] text-blue-700 dark:text-[#38bdf8] border border-blue-200 dark:border-[#1d4370] px-2.5 py-0.5 text-xs font-semibold">
              {{ store.currentComplaint.category }}
            </span>
            <span class="rounded-lg bg-slate-100 dark:bg-[#1e1e1e] text-slate-700 dark:text-[#cccccc] border border-slate-200 dark:border-[#383838] px-2 py-0.5 text-xs font-mono font-medium">
              {{ store.currentComplaint.current_bureau_code }}
            </span>
            <StatusBadge :status="store.currentComplaint.status" variant="tag" />
            <PriorityBadge :priority="store.currentComplaint.priority" variant="tag" />
            <span
              v-if="store.currentComplaint.is_overdue"
              class="rounded-lg bg-red-100 text-red-800 dark:bg-[#3b1214] dark:text-[#f48771] border border-red-300 dark:border-[#5c1c20] text-xs font-bold px-2 py-0.5"
            >
              Overdue
            </span>
          </div>
          <p class="text-xs text-slate-500 dark:text-[#989898] mt-1.5 [text-wrap:pretty]">
            Registered on {{ store.currentComplaint.received_at?.slice(0, 10) }} · Last action on {{ store.currentComplaint.last_action_at?.slice(0, 10) }}
          </p>
        </div>

        <!-- Action Buttons (Disabled if unauthorized) -->
        <div v-if="canEdit" class="flex flex-wrap items-center gap-2">
          <button
            type="button"
            class="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-50 dark:hover:bg-[#37373d] transition shadow-sm"
            @click="isAssignModalOpen = true"
          >
            <UserCheck class="w-3.5 h-3.5 text-slate-500 dark:text-[#989898]" />
            Assign Officer
          </button>

          <button
            type="button"
            class="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-50 dark:hover:bg-[#37373d] transition shadow-sm"
            @click="isTransferModalOpen = true"
          >
            <Send class="w-3.5 h-3.5 text-slate-500 dark:text-[#989898]" />
            Transfer Bureau
          </button>

          <button
            type="button"
            class="inline-flex items-center gap-1.5 rounded-lg bg-[#f97316] hover:bg-[#ea580c] px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm transition-all"
            @click="isStatusModalOpen = true"
          >
            <FileCheck2 class="w-3.5 h-3.5" />
            Update Status
          </button>
        </div>
        <div v-else class="text-xs text-slate-400 dark:text-[#989898]">
          {{ authStore.isSeniorAuthority ? 'Read-only view' : 'Only the responsible bureau can modify this complaint' }}
        </div>
      </div>
    </div>

    <!-- Overview Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Target Institution Card -->
      <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-4">
        <p class="text-xs font-medium text-slate-400 dark:text-[#989898]">
          Institution
        </p>
        <router-link
          :to="`/institutions/${store.currentComplaint.institution_id}`"
          class="mt-1 block font-medium text-sm text-slate-900 dark:text-[#d4d4d4] hover:text-blue-600 dark:hover:text-[#4fc1ff] transition"
        >
          {{ store.currentComplaint.institution_name }}
        </router-link>
        <p class="text-xs text-slate-500 dark:text-[#989898] mt-1 font-mono">
          AICTE ID: {{ store.currentComplaint.institution_code }}
        </p>
        <p class="text-xs text-slate-500 dark:text-[#989898]">
          State: {{ store.currentComplaint.institution_state }}
        </p>
      </div>

      <!-- Department Ownership Card -->
      <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-4">
        <p class="text-xs font-medium text-slate-400 dark:text-[#989898]">
          Assigned Bureau
        </p>
        <div class="mt-1 flex items-center gap-2">
          <span class="rounded bg-slate-900 dark:bg-[#2d2d2d] text-amber-400 dark:text-[#cca700] px-2 py-0.5 text-xs font-medium border border-slate-700 dark:border-[#3e3e42]">
            {{ store.currentComplaint.current_bureau_code }}
          </span>
          <span class="text-xs font-medium text-slate-800 dark:text-[#cccccc]">
            {{ store.currentComplaint.current_bureau_name }}
          </span>
        </div>
        <p class="text-xs text-slate-500 dark:text-[#989898] mt-1">
          Receiving bureau: {{ store.currentComplaint.receiving_bureau_code }}
        </p>
        <p class="text-xs text-slate-700 dark:text-[#cccccc]">
          Assigned officer: {{ store.currentComplaint.assigned_officer_name || 'Unassigned' }}
        </p>
      </div>

      <!-- Deadlines Card -->
      <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-4">
        <p class="text-xs font-medium text-slate-400 dark:text-[#989898]">
          Resolution Deadline
        </p>
        <div class="mt-1 flex items-baseline gap-2">
          <span class="text-sm font-medium text-slate-900 dark:text-[#d4d4d4]">
            Due: {{ store.currentComplaint.due_at ? store.currentComplaint.due_at.slice(0, 10) : 'N/A' }}
          </span>
        </div>
        <p v-if="store.currentComplaint.is_overdue" class="text-xs font-medium text-red-600 dark:text-[#f48771] mt-1 flex items-center gap-1">
          <Clock class="w-3.5 h-3.5" />
          Response overdue
        </p>
        <p v-else class="text-xs text-emerald-600 dark:text-[#89d185] mt-1 font-medium">
          Within deadline
        </p>
        <p v-if="store.currentComplaint.external_reference" class="text-xs text-slate-400 dark:text-[#989898] mt-1">
          Ref: {{ store.currentComplaint.external_reference }}
        </p>
      </div>
    </div>

    <!-- Continuous Tabs -->
    <div class="border-b border-slate-200 dark:border-[#2d2d2d]">
      <nav class="flex gap-6 -mb-px text-xs font-medium">
        <button
          type="button"
          :class="[
            'pb-2.5 border-b-2 transition flex items-center gap-2',
            activeTab === 'overview'
              ? 'border-slate-900 dark:border-[#007acc] text-slate-900 dark:text-white'
              : 'border-transparent text-slate-500 dark:text-[#989898] hover:text-slate-800 dark:hover:text-[#cccccc]'
          ]"
          @click="activeTab = 'overview'"
        >
          Overview
        </button>

        <button
          type="button"
          :class="[
            'pb-2.5 border-b-2 transition flex items-center gap-2',
            activeTab === 'timeline'
              ? 'border-slate-900 dark:border-[#007acc] text-slate-900 dark:text-white'
              : 'border-transparent text-slate-500 dark:text-[#989898] hover:text-slate-800 dark:hover:text-[#cccccc]'
          ]"
          @click="activeTab = 'timeline'"
        >
          Activity History
          <span class="rounded bg-slate-100 dark:bg-[#2d2d2d] text-slate-700 dark:text-[#cccccc] px-1.5 py-0.5 text-xs">
            {{ store.currentComplaint.actions?.length || 0 }}
          </span>
        </button>

        <button
          type="button"
          :class="[
            'pb-2.5 border-b-2 transition flex items-center gap-2',
            activeTab === 'overlaps'
              ? 'border-slate-900 dark:border-[#007acc] text-slate-900 dark:text-white'
              : 'border-transparent text-slate-500 dark:text-[#989898] hover:text-slate-800 dark:hover:text-[#cccccc]'
          ]"
          @click="activeTab = 'overlaps'"
        >
          Related Cases
          <span
            v-if="(store.currentComplaint.related_links?.length || 0) > 0"
            class="rounded bg-[#cca700]/20 text-[#cca700] font-medium px-1.5 py-0.5 text-xs"
          >
            {{ store.currentComplaint.related_links?.length }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Tab 1: Overview -->
    <div v-if="activeTab === 'overview'" class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-5 space-y-5">
      <div>
        <h2 class="text-xs font-medium text-slate-400 dark:text-[#989898]">Subject</h2>
        <p class="text-sm font-medium text-slate-900 dark:text-[#d4d4d4] mt-1">
          {{ store.currentComplaint.subject }}
        </p>
      </div>

      <div class="border-t border-slate-100 dark:border-[#2d2d2d] pt-4">
        <h2 class="text-xs font-medium text-slate-400 dark:text-[#989898]">Description</h2>
        <div class="mt-2 text-xs leading-relaxed text-slate-700 dark:text-[#cccccc] bg-slate-50 dark:bg-[#1e1e1e] p-4 rounded border border-slate-200 dark:border-[#2d2d2d] whitespace-pre-wrap font-sans">
          {{ store.currentComplaint.description }}
        </div>
      </div>

      <div v-if="store.currentComplaint.resolution_summary" class="border-t border-slate-100 dark:border-[#2d2d2d] pt-4">
        <h2 class="text-xs font-medium text-emerald-700 dark:text-[#89d185] flex items-center gap-1.5">
          <CheckCircle2 class="w-4 h-4" />
          Resolution Notes
        </h2>
        <div class="mt-2 text-xs leading-relaxed text-emerald-900 dark:text-[#89d185] bg-emerald-50 dark:bg-[#89d185]/10 p-4 rounded border border-emerald-200 dark:border-[#89d185]/20">
          {{ store.currentComplaint.resolution_summary }}
        </div>
      </div>
    </div>

    <!-- Tab 2: Action Timeline -->
    <div v-else-if="activeTab === 'timeline'" class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-5">
      <div class="border-b border-slate-100 dark:border-[#2d2d2d] pb-3 mb-6">
        <h2 class="text-xs font-medium text-slate-800 dark:text-[#cccccc]">
          Action History
        </h2>
        <p class="text-xs text-slate-500 dark:text-[#989898]">
          Chronological record of status changes, bureau transfers, and officer updates
        </p>
      </div>

      <div class="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-[#2d2d2d]">
        <div
          v-for="act in store.currentComplaint.actions"
          :key="act.id"
          class="relative"
        >
          <!-- Bullet dot -->
          <div class="absolute -left-6 top-1.5 w-2.5 h-2.5 rounded-full bg-slate-900 dark:bg-[#007acc] ring-4 ring-white dark:ring-[#252526]" />

          <div class="bg-slate-50 dark:bg-[#1e1e1e] p-3.5 rounded border border-slate-200 dark:border-[#2d2d2d]">
            <div class="flex items-center justify-between gap-2">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-200 dark:bg-[#2d2d2d] text-slate-800 dark:text-[#cccccc]">
                {{ act.action_type.replace('_', ' ') }}
              </span>
              <span class="text-xs text-slate-400 dark:text-[#989898]">
                {{ act.created_at?.slice(0, 16).replace('T', ' ') }}
              </span>
            </div>

            <p class="text-xs text-slate-800 dark:text-[#cccccc] mt-2 font-medium">
              {{ act.description }}
            </p>

            <div class="mt-2 text-xs text-slate-500 dark:text-[#989898] flex flex-wrap items-center gap-3">
              <span>By: <strong class="text-slate-700 dark:text-[#cccccc]">{{ act.performed_by_name }}</strong></span>
              <span v-if="act.old_status && act.new_status">
                Status: {{ act.old_status }} → <strong class="text-slate-700 dark:text-[#cccccc]">{{ act.new_status }}</strong>
              </span>
              <span v-if="act.old_bureau_code && act.new_bureau_code && act.old_bureau_code !== act.new_bureau_code">
                Bureau: {{ act.old_bureau_code }} → <strong class="text-slate-700 dark:text-[#cccccc]">{{ act.new_bureau_code }}</strong>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 3: Related Overlaps -->
    <div v-else-if="activeTab === 'overlaps'" class="space-y-4">
      <div v-if="(store.currentComplaint.related_links?.length || 0) === 0" class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-6 text-center text-xs text-slate-500 dark:text-[#989898]">
        No related cases detected for this complaint.
      </div>

      <div
        v-for="link in store.currentComplaint.related_links"
        :key="link.id"
        class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-4 space-y-3"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-2">
            <span class="rounded bg-[#cca700]/20 text-[#cca700] px-2 py-0.5 text-xs font-medium">
              {{ Math.round(link.match_score * 100) }}% match
            </span>
            <span class="text-xs text-slate-500 dark:text-[#989898]">
              Method: {{ link.match_method }}
            </span>
            <span
              :class="[
                'text-xs font-medium px-2 py-0.5 rounded',
                link.review_status === 'confirmed' ? 'bg-[#89d185]/20 text-[#89d185]' :
                link.review_status === 'dismissed' ? 'bg-slate-200 dark:bg-[#2d2d2d] text-slate-700 dark:text-[#989898]' :
                'bg-[#cca700]/20 text-[#cca700]'
              ]"
            >
              {{ link.review_status }}
            </span>
          </div>

          <router-link
            to="/overlaps"
            class="text-xs font-medium text-blue-600 dark:text-[#4fc1ff] hover:underline flex items-center gap-1"
          >
            Review in overlap queue
            <ExternalLink class="w-3.5 h-3.5" />
          </router-link>
        </div>

        <p class="text-xs text-slate-700 dark:text-[#cccccc] bg-amber-50/60 dark:bg-[#1e1e1e] p-3 rounded border border-amber-200/60 dark:border-[#2d2d2d]">
          <strong class="text-slate-800 dark:text-white">Match reason:</strong> {{ link.match_reason }}
        </p>

        <!-- Correlated other case snapshot -->
        <div v-if="link.other_case" class="p-3 rounded border border-slate-200 dark:border-[#2d2d2d] bg-slate-50 dark:bg-[#1e1e1e]">
          <p class="text-xs font-medium text-slate-400 dark:text-[#989898]">
            Matching complaint
          </p>
          <div class="flex items-center justify-between mt-1">
            <router-link
              :to="`/complaints/${link.other_case.id}`"
              class="font-mono font-medium text-xs text-blue-600 dark:text-[#4fc1ff] hover:underline"
            >
              {{ link.other_case.case_number }}
            </router-link>
            <div class="flex items-center gap-2">
              <span class="rounded bg-slate-200 dark:bg-[#2d2d2d] px-1.5 py-0.5 text-xs font-medium text-slate-800 dark:text-[#cccccc]">
                {{ link.other_case.bureau_code }}
              </span>
              <StatusBadge :status="link.other_case.status" size="sm" />
            </div>
          </div>
          <p class="text-xs font-medium text-slate-800 dark:text-[#cccccc] mt-1">
            {{ link.other_case.subject }}
          </p>
          <p class="text-xs text-slate-500 dark:text-[#989898] line-clamp-2 mt-0.5">
            {{ link.other_case.description }}
          </p>
        </div>
      </div>
    </div>

    <!-- Modal: Update Status -->
    <Modal
      :is-open="isStatusModalOpen"
      title="Update Status"
      @close="isStatusModalOpen = false"
    >
      <form class="space-y-4" @submit.prevent="handleUpdateStatus">
        <div v-if="actionError" class="p-3 rounded bg-red-50 dark:bg-[#f48771]/15 text-xs text-red-700 dark:text-[#f48771] border border-red-200 dark:border-[#f48771]/30">
          {{ actionError }}
        </div>

        <div>
          <label for="modal-status-select" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">New status *</label>
          <select
            id="modal-status-select"
            v-model="newStatus"
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc] focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc]"
          >
            <option value="Under Review">Under Review</option>
            <option value="Action Required">Action Required</option>
            <option value="Awaiting Response">Awaiting Response</option>
            <option value="Escalated">Escalated</option>
            <option value="Disposed">Disposed (Resolved)</option>
            <option value="Closed">Closed (Concluded)</option>
          </select>
        </div>

        <div>
          <label for="modal-status-remarks" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">
            Action description or remarks *
          </label>
          <textarea
            id="modal-status-remarks"
            v-model="statusRemarks"
            rows="3"
            required
            placeholder="Record regulatory steps, notices issued, hearing dates, or resolution notes..."
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc] focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc]"
          />
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          class="px-3 py-1.5 rounded border border-slate-300 dark:border-[#3e3e42] text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-100 dark:hover:bg-[#37373d]"
          @click="isStatusModalOpen = false"
        >
          Cancel
        </button>
        <button
          type="button"
          :disabled="isActionLoading"
          class="px-4 py-1.5 rounded bg-slate-900 dark:bg-[#007acc] text-xs font-medium text-white hover:bg-slate-800 dark:hover:bg-[#1177bb] disabled:opacity-50"
          @click="handleUpdateStatus"
        >
          Update Status
        </button>
      </template>
    </Modal>

    <!-- Modal: Assign Officer -->
    <Modal
      :is-open="isAssignModalOpen"
      title="Assign Bureau Officer"
      @close="isAssignModalOpen = false"
    >
      <form class="space-y-4" @submit.prevent="handleAssignOfficer">
        <div v-if="actionError" class="p-3 rounded bg-red-50 dark:bg-[#f48771]/15 text-xs text-red-700 dark:text-[#f48771] border border-red-200 dark:border-[#f48771]/30">
          {{ actionError }}
        </div>

        <div>
          <label for="modal-assign-officer" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Select officer *</label>
          <select
            id="modal-assign-officer"
            v-model="selectedOfficerId"
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc] focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc]"
          >
            <option value="">-- Unassigned --</option>
            <option v-for="off in bureauOfficers" :key="off.id" :value="off.id">
              {{ off.name }} ({{ off.designation || off.role }})
            </option>
          </select>
        </div>

        <div>
          <label for="modal-assign-remarks" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Instructions or remarks</label>
          <textarea
            id="modal-assign-remarks"
            v-model="assignRemarks"
            rows="2"
            placeholder="Instructions for the assigned officer..."
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc] focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc]"
          />
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          class="px-3 py-1.5 rounded border border-slate-300 dark:border-[#3e3e42] text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-100 dark:hover:bg-[#37373d]"
          @click="isAssignModalOpen = false"
        >
          Cancel
        </button>
        <button
          type="button"
          :disabled="isActionLoading"
          class="px-4 py-1.5 rounded bg-slate-900 dark:bg-[#007acc] text-xs font-medium text-white hover:bg-slate-800 dark:hover:bg-[#1177bb] disabled:opacity-50"
          @click="handleAssignOfficer"
        >
          Assign Officer
        </button>
      </template>
    </Modal>

    <!-- Modal: Transfer Bureau -->
    <Modal
      :is-open="isTransferModalOpen"
      title="Transfer Bureau"
      @close="isTransferModalOpen = false"
    >
      <form class="space-y-4" @submit.prevent="handleTransferBureau">
        <div v-if="actionError" class="p-3 rounded bg-red-50 dark:bg-[#f48771]/15 text-xs text-red-700 dark:text-[#f48771] border border-red-200 dark:border-[#f48771]/30">
          {{ actionError }}
        </div>

        <div>
          <label for="modal-transfer-bureau" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Destination bureau *</label>
          <select
            id="modal-transfer-bureau"
            v-model="selectedTargetBureauId"
            required
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc] focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc]"
          >
            <option value="">-- Select Destination Bureau --</option>
            <option
              v-for="b in bureaus.filter(b => b.id !== store.currentComplaint?.current_bureau_id)"
              :key="b.id"
              :value="b.id"
            >
              {{ b.code }}: {{ b.name }}
            </option>
          </select>
        </div>

        <div>
          <label for="modal-transfer-reason" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Transfer justification *</label>
          <textarea
            id="modal-transfer-reason"
            v-model="transferRemarks"
            rows="3"
            required
            placeholder="Explain why this complaint falls under the destination bureau's jurisdiction..."
            class="mt-1 block w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc] focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc]"
          />
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          class="px-3 py-1.5 rounded border border-slate-300 dark:border-[#3e3e42] text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-100 dark:hover:bg-[#37373d]"
          @click="isTransferModalOpen = false"
        >
          Cancel
        </button>
        <button
          type="button"
          :disabled="isActionLoading"
          class="px-4 py-1.5 rounded bg-slate-900 dark:bg-[#007acc] text-xs font-medium text-white hover:bg-slate-800 dark:hover:bg-[#1177bb] disabled:opacity-50"
          @click="handleTransferBureau"
        >
          Transfer Complaint
        </button>
      </template>
    </Modal>
  </div>

  <!-- Loading Skeleton -->
  <div v-else-if="store.loading" class="space-y-6 animate-pulse">
    <div class="h-4 bg-slate-200 dark:bg-[#2d2d2d] rounded w-1/4"></div>
    <div class="rounded-xl border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-6 space-y-4">
      <div class="h-6 bg-slate-200 dark:bg-[#2d2d2d] rounded w-2/5"></div>
      <div class="h-4 bg-slate-200 dark:bg-[#2d2d2d] rounded w-3/5"></div>
      <div class="h-24 bg-slate-100 dark:bg-[#1e1e1e] rounded w-full"></div>
    </div>
  </div>

  <!-- Not Found State -->
  <div v-else class="rounded-xl border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-12 text-center space-y-4">
    <div class="inline-flex p-3 rounded-full bg-red-50 dark:bg-[#3b1214] text-red-600 dark:text-[#f48771]">
      <AlertCircle class="w-6 h-6" />
    </div>
    <h2 class="text-base font-semibold text-slate-900 dark:text-white">Complaint Not Found</h2>
    <p class="text-xs text-slate-500 dark:text-[#989898] max-w-sm mx-auto [text-wrap:pretty]">
      The requested grievance case could not be located. It may have been archived, transferred, or does not exist.
    </p>
    <div>
      <router-link
        to="/complaints"
        class="inline-flex items-center gap-1.5 rounded-lg bg-[#c2410c] hover:bg-[#9a3412] px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all"
      >
        <ArrowLeft class="w-3.5 h-3.5" />
        Back to Complaints Registry
      </router-link>
    </div>
  </div>
</template>
