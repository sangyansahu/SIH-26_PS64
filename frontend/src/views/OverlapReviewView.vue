<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useOverlapsStore } from '@/stores/overlaps'
import { useAuthStore } from '@/stores/auth'
import StatusBadge from '@/components/StatusBadge.vue'
import PriorityBadge from '@/components/PriorityBadge.vue'
import Modal from '@/components/Modal.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { CaseLink } from '@/types'
import {
  GitCompare,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  ExternalLink,
  RefreshCw,
  Tag,
  Building,
  ShieldAlert,
} from 'lucide-vue-next'

const store = useOverlapsStore()
const authStore = useAuthStore()

const currentTab = ref<'pending' | 'confirmed' | 'dismissed' | 'deferred'>('pending')

// Review Modal State
const isReviewModalOpen = ref(false)
const selectedLink = ref<CaseLink | null>(null)
const reviewDecision = ref<'confirmed_related' | 'unrelated' | 'deferred'>('confirmed_related')
const reviewRemarks = ref('')
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)

onMounted(() => {
  store.fetchOverlaps(currentTab.value)
})

function switchTab(tab: 'pending' | 'confirmed' | 'dismissed' | 'deferred') {
  currentTab.value = tab
  store.fetchOverlaps(tab)
}

function openReviewModal(link: CaseLink, decision: 'confirmed_related' | 'unrelated' | 'deferred') {
  selectedLink.value = link
  reviewDecision.value = decision
  reviewRemarks.value = ''
  submitError.value = null
  isReviewModalOpen.value = true
}

async function handleConfirmReview() {
  if (!selectedLink.value) return
  isSubmitting.value = true
  submitError.value = null

  const res = await store.reviewOverlap(
    selectedLink.value.id,
    reviewDecision.value,
    reviewRemarks.value
  )

  isSubmitting.value = false
  if (res.success) {
    isReviewModalOpen.value = false
  } else {
    submitError.value = res.error
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">
          Cross-Bureau Overlaps
        </h1>
        <p class="text-xs text-slate-500 dark:text-[#989898] mt-0.5">
          Cases flagged across bureaus for matching institutions, external dockets, or related issues
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          v-if="authStore.isAdmin"
          type="button"
          :disabled="store.loading"
          class="inline-flex items-center gap-1.5 rounded border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-50 dark:hover:bg-[#37373d] disabled:opacity-50 transition-colors"
          @click="store.rescanAll()"
        >
          <RefreshCw :class="['w-3.5 h-3.5', store.loading ? 'animate-spin' : '']" aria-hidden="true" />
          Re-scan All Records
        </button>
      </div>
    </div>

    <!-- Engine Matching Criteria Box -->
    <div class="rounded-md border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-4">
      <h2 class="text-xs font-semibold uppercase tracking-wider text-slate-800 dark:text-white">
        Matching Criteria
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-slate-100 dark:divide-[#2d2d2d] mt-3 pt-3 border-t border-slate-100 dark:border-[#2d2d2d]">
        <div class="py-2 sm:py-0 sm:px-3 first:pl-0 last:pr-0">
          <p class="font-medium text-slate-900 dark:text-white">1. Direct Identifiers</p>
          <p class="text-xs text-slate-500 dark:text-[#989898] mt-1 leading-relaxed [text-wrap:pretty]">
            Permanent Institute ID and external reference numbers including CPGRAMS or court dockets.
          </p>
        </div>
        <div class="py-2 sm:py-0 sm:px-3 first:pl-0 last:pr-0">
          <p class="font-medium text-slate-900 dark:text-white">2. Institution Resolution</p>
          <p class="text-xs text-slate-500 dark:text-[#989898] mt-1 leading-relaxed [text-wrap:pretty]">
            Normalized college names, known campus aliases, and state boundaries.
          </p>
        </div>
        <div class="py-2 sm:py-0 sm:px-3 first:pl-0 last:pr-0">
          <p class="font-medium text-slate-900 dark:text-white">3. Content Similarity</p>
          <p class="text-xs text-slate-500 dark:text-[#989898] mt-1 leading-relaxed [text-wrap:pretty]">
            Shared grievance category, keywords, and core incident descriptions.
          </p>
        </div>
        <div class="py-2 sm:py-0 sm:px-3 first:pl-0 last:pr-0">
          <p class="font-medium text-slate-900 dark:text-white">4. Officer Review</p>
          <p class="text-xs text-slate-500 dark:text-[#989898] mt-1 leading-relaxed [text-wrap:pretty]">
            Participating bureau officers confirm correlation, dismiss, or order joint inquiry.
          </p>
        </div>
      </div>
    </div>

    <!-- Review Status Tabs -->
    <div class="flex items-center gap-2 border-b border-slate-200 dark:border-[#2d2d2d] pb-2">
      <button
        type="button"
        :class="[
          'px-3 py-1.5 rounded text-xs font-medium transition-colors flex items-center gap-2',
          currentTab === 'pending'
            ? 'bg-slate-900 dark:bg-[#37373d] text-white'
            : 'bg-white dark:bg-[#252526] text-slate-600 dark:text-[#989898] hover:bg-slate-100 dark:hover:bg-[#2a2d2e] dark:hover:text-[#cccccc] border border-slate-200 dark:border-[#2d2d2d]'
        ]"
        @click="switchTab('pending')"
      >
        <span>Pending Review</span>
        <span
          v-if="store.pendingCount > 0"
          class="rounded bg-amber-600 dark:bg-[#cca700] text-white dark:text-[#1e1e1e] font-semibold px-1.5 py-0.2 text-xs tabular-nums"
        >
          {{ store.pendingCount }}
        </span>
      </button>

      <button
        type="button"
        :class="[
          'px-3 py-1.5 rounded text-xs font-medium transition-colors',
          currentTab === 'confirmed'
            ? 'bg-slate-900 dark:bg-[#37373d] text-white'
            : 'bg-white dark:bg-[#252526] text-slate-600 dark:text-[#989898] hover:bg-slate-100 dark:hover:bg-[#2a2d2e] dark:hover:text-[#cccccc] border border-slate-200 dark:border-[#2d2d2d]'
        ]"
        @click="switchTab('confirmed')"
      >
        Confirmed Related
      </button>

      <button
        type="button"
        :class="[
          'px-3 py-1.5 rounded text-xs font-medium transition-colors',
          currentTab === 'dismissed'
            ? 'bg-slate-900 dark:bg-[#37373d] text-white'
            : 'bg-white dark:bg-[#252526] text-slate-600 dark:text-[#989898] hover:bg-slate-100 dark:hover:bg-[#2a2d2e] dark:hover:text-[#cccccc] border border-slate-200 dark:border-[#2d2d2d]'
        ]"
        @click="switchTab('dismissed')"
      >
        Marked Unrelated
      </button>

      <button
        type="button"
        :class="[
          'px-3 py-1.5 rounded text-xs font-medium transition-colors',
          currentTab === 'deferred'
            ? 'bg-slate-900 dark:bg-[#37373d] text-white'
            : 'bg-white dark:bg-[#252526] text-slate-600 dark:text-[#989898] hover:bg-slate-100 dark:hover:bg-[#2a2d2e] dark:hover:text-[#cccccc] border border-slate-200 dark:border-[#2d2d2d]'
        ]"
        @click="switchTab('deferred')"
      >
        Deferred
      </button>
    </div>

    <!-- Overlap Pairs Queue -->
    <div class="space-y-4">
      <div
        v-for="link in store.overlaps"
        :key="link.id"
        class="rounded-md border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] overflow-hidden"
      >
        <!-- Card Header: Score, Method & Actions -->
        <div class="bg-slate-50 dark:bg-[#2d2d2d] border-b border-slate-200 dark:border-[#2d2d2d] px-5 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div class="flex items-center gap-2.5">
            <span class="rounded bg-amber-600 dark:bg-[#cca700] text-white dark:text-[#1e1e1e] px-2 py-0.5 text-xs font-semibold tabular-nums">
              {{ Math.round(link.match_score * 100) }}% match
            </span>

            <span class="text-xs font-mono text-slate-600 dark:text-[#989898]">
              Method: {{ link.match_method }}
            </span>

            <span
              :class="[
                'text-xs font-medium px-2 py-0.5 rounded uppercase',
                link.review_status === 'confirmed' ? 'bg-emerald-100 dark:bg-[#122e1b] text-emerald-800 dark:text-[#89d185] border border-emerald-300 dark:border-[#1f4a2b]' :
                link.review_status === 'dismissed' ? 'bg-slate-200 dark:bg-[#1e1e1e] text-slate-700 dark:text-[#989898] border border-slate-300 dark:border-[#3e3e42]' :
                link.review_status === 'deferred' ? 'bg-purple-100 dark:bg-[#3b1c47] text-purple-800 dark:text-[#c586c0] border border-purple-300 dark:border-[#562868]' :
                'bg-amber-100 dark:bg-[#332b00] text-amber-800 dark:text-[#cca700] border border-amber-300 dark:border-[#554400]'
              ]"
            >
              {{ link.review_status }}
            </span>
          </div>

          <!-- Official Action Buttons (for authorized officers / admins) -->
          <div v-if="!authStore.isSeniorAuthority" class="flex items-center gap-2">
            <button
              v-if="link.review_status !== 'confirmed'"
              type="button"
              class="inline-flex items-center gap-1 rounded bg-emerald-700 dark:bg-[#1b3b22] dark:border dark:border-[#25582f] px-2.5 py-1 text-xs font-medium text-white dark:text-[#89d185] hover:bg-emerald-800 dark:hover:bg-[#25582f] transition-colors"
              @click="openReviewModal(link, 'confirmed_related')"
            >
              <CheckCircle2 class="w-3.5 h-3.5" aria-hidden="true" />
              Confirm Related
            </button>

            <button
              v-if="link.review_status !== 'dismissed'"
              type="button"
              class="inline-flex items-center gap-1 rounded border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-2.5 py-1 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-100 dark:hover:bg-[#37373d] transition-colors"
              @click="openReviewModal(link, 'unrelated')"
            >
              <XCircle class="w-3.5 h-3.5 text-slate-500 dark:text-[#989898]" aria-hidden="true" />
              Mark Unrelated
            </button>

            <button
              v-if="link.review_status !== 'deferred'"
              type="button"
              class="inline-flex items-center gap-1 rounded border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-2.5 py-1 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-100 dark:hover:bg-[#37373d] transition-colors"
              @click="openReviewModal(link, 'deferred')"
            >
              <Clock class="w-3.5 h-3.5 text-slate-500 dark:text-[#989898]" aria-hidden="true" />
              Defer
            </button>
          </div>
        </div>

        <!-- Rationale & Signals Breakdown -->
        <div class="px-5 py-3 bg-amber-50/50 dark:bg-[#332b00]/30 border-b border-amber-100 dark:border-[#554400]/40">
          <p class="text-xs text-amber-950 dark:text-[#d7ba7d] leading-relaxed">
            <span class="font-semibold">Match reason:</span> {{ link.match_reason }}
          </p>

          <!-- Evidence Badges -->
          <div class="mt-2 flex flex-wrap items-center gap-1.5 text-xs">
            <span
              v-if="link.evidence.same_institution_id"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-100 dark:bg-[#122e1b] text-emerald-800 dark:text-[#89d185] border border-emerald-200 dark:border-[#1f4a2b]"
            >
              <Building class="w-3 h-3" aria-hidden="true" />
              Matching Permanent Institute ID
            </span>

            <span
              v-if="link.evidence.same_external_reference"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-100 dark:bg-[#093554] text-blue-800 dark:text-[#4fc1ff] border border-blue-200 dark:border-[#14496b]"
            >
              Matching External Docket Reference
            </span>

            <span
              v-if="link.evidence.cross_bureau"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-purple-100 dark:bg-[#3b1c47] text-purple-800 dark:text-[#c586c0] border border-purple-200 dark:border-[#562868]"
            >
              Cross-Bureau
            </span>

            <!-- Salient Keywords -->
            <div
              v-if="link.evidence.shared_keywords && link.evidence.shared_keywords.length > 0"
              class="flex items-center gap-1 ml-2"
            >
              <span class="text-slate-500 dark:text-[#989898]">Keywords:</span>
              <span
                v-for="kw in link.evidence.shared_keywords"
                :key="kw"
                class="rounded bg-white dark:bg-[#1e1e1e] border border-slate-200 dark:border-[#3e3e42] px-1.5 py-0.2 text-xs font-mono text-slate-700 dark:text-[#cccccc]"
              >
                #{{ kw }}
              </span>
            </div>
          </div>

          <!-- Review audit info if already reviewed -->
          <div v-if="link.reviewed_by_name" class="mt-2 pt-2 border-t border-amber-200/50 dark:border-[#554400]/40 text-xs text-slate-600 dark:text-[#989898] flex items-center gap-3">
            <span>Reviewed by: <strong class="dark:text-[#cccccc]">{{ link.reviewed_by_name }}</strong></span>
            <span>Date: {{ link.reviewed_at?.slice(0, 16).replace('T', ' ') }}</span>
            <span v-if="link.review_remarks">Remarks: <em>"{{ link.review_remarks }}"</em></span>
          </div>
        </div>

        <!-- Side-by-Side Comparison Columns -->
        <div class="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200 dark:divide-[#2d2d2d]">
          <!-- Case A Card -->
          <div v-if="link.case_a" class="p-5 space-y-2.5 bg-white dark:bg-[#252526]">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-[#989898]">Case A (Primary)</span>
              <span class="rounded bg-slate-100 dark:bg-[#1e1e1e] px-2 py-0.5 text-xs font-semibold text-slate-700 dark:text-[#4fc1ff] border border-slate-200 dark:border-[#3e3e42]">
                {{ link.case_a.bureau_code }}
              </span>
            </div>

            <div>
              <router-link
                :to="`/complaints/${link.case_a.id}`"
                class="font-mono text-xs font-bold text-blue-600 dark:text-[#4fc1ff] hover:underline flex items-center gap-1"
              >
                {{ link.case_a.case_number }}
                <ExternalLink class="w-3 h-3" aria-hidden="true" />
              </router-link>
              <p class="text-xs font-medium text-slate-900 dark:text-white mt-1">
                {{ link.case_a.institution_name }} ({{ link.case_a.institution_code }})
              </p>
            </div>

            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-600 dark:text-[#989898]">{{ link.case_a.category }}</span>
              <span>·</span>
              <PriorityBadge :priority="link.case_a.priority" size="sm" />
              <StatusBadge :status="link.case_a.status" size="sm" />
            </div>

            <p class="text-xs font-semibold text-slate-800 dark:text-[#cccccc]">
              {{ link.case_a.subject }}
            </p>

            <p class="text-xs text-slate-600 dark:text-[#989898] leading-relaxed [text-wrap:pretty] mt-1">
              {{ link.case_a.description }}
            </p>
          </div>

          <!-- Case B Card -->
          <div v-if="link.case_b" class="p-5 space-y-2.5 bg-white dark:bg-[#252526]">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-[#989898]">Case B (Comparison)</span>
              <span class="rounded bg-slate-100 dark:bg-[#1e1e1e] px-2 py-0.5 text-xs font-semibold text-slate-700 dark:text-[#4fc1ff] border border-slate-200 dark:border-[#3e3e42]">
                {{ link.case_b.bureau_code }}
              </span>
            </div>

            <div>
              <router-link
                :to="`/complaints/${link.case_b.id}`"
                class="font-mono text-xs font-bold text-blue-600 dark:text-[#4fc1ff] hover:underline flex items-center gap-1"
              >
                {{ link.case_b.case_number }}
                <ExternalLink class="w-3 h-3" aria-hidden="true" />
              </router-link>
              <p class="text-xs font-medium text-slate-900 dark:text-white mt-1">
                {{ link.case_b.institution_name }} ({{ link.case_b.institution_code }})
              </p>
            </div>

            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-600 dark:text-[#989898]">{{ link.case_b.category }}</span>
              <span>·</span>
              <PriorityBadge :priority="link.case_b.priority" size="sm" />
              <StatusBadge :status="link.case_b.status" size="sm" />
            </div>

            <p class="text-xs font-semibold text-slate-800 dark:text-[#cccccc]">
              {{ link.case_b.subject }}
            </p>

            <p class="text-xs text-slate-600 dark:text-[#989898] leading-relaxed [text-wrap:pretty] mt-1">
              {{ link.case_b.description }}
            </p>
          </div>
        </div>
      </div>

      <div v-if="store.overlaps.length === 0 && !store.loading">
        <EmptyState
          title="No records in this queue"
          description="Any potential overlap flagged across bureaus will appear here for review."
        />
      </div>
    </div>

    <!-- Official Review Modal Dialog -->
    <Modal
      :is-open="isReviewModalOpen"
      :title="`Record Decision: ${reviewDecision.replace('_', ' ').toUpperCase()}`"
      @close="isReviewModalOpen = false"
    >
      <form class="space-y-4" @submit.prevent="handleConfirmReview">
        <div v-if="submitError" class="p-3 rounded bg-red-50 dark:bg-[#3b1214] text-xs text-red-700 dark:text-[#f48771] border border-red-200 dark:border-[#5c1c20]" role="alert">
          {{ submitError }}
        </div>

        <div class="rounded bg-slate-50 dark:bg-[#1e1e1e] p-3 border border-slate-200 dark:border-[#2d2d2d] text-xs">
          <p class="font-semibold text-slate-900 dark:text-white">
            Comparing: {{ selectedLink?.case_a?.case_number }} ({{ selectedLink?.case_a?.bureau_code }})
            vs {{ selectedLink?.case_b?.case_number }} ({{ selectedLink?.case_b?.bureau_code }})
          </p>
          <p class="text-slate-500 dark:text-[#989898] mt-0.5">
            Institution: {{ selectedLink?.case_a?.institution_name }}
          </p>
        </div>

        <div>
          <label for="review-decision" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Decision *</label>
          <select
            id="review-decision"
            v-model="reviewDecision"
            class="mt-1 block w-full px-3 py-2 text-xs border border-slate-300 dark:border-[#3e3e42] rounded bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc]"
          >
            <option value="confirmed_related">Confirmed Related (Coordinate joint review across bureaus)</option>
            <option value="unrelated">Mark Unrelated (Complaints cover distinct non-overlapping matters)</option>
            <option value="deferred">Defer Decision (Awaiting departmental preliminary verification)</option>
          </select>
        </div>

        <div>
          <label for="review-remarks" class="block text-xs font-medium text-slate-700 dark:text-[#cccccc]">Review Remarks *</label>
          <textarea
            id="review-remarks"
            v-model="reviewRemarks"
            rows="3"
            required
            placeholder="Record review notes or coordination directives for participating bureaus…"
            class="mt-1 block w-full px-3 py-2 text-xs border border-slate-300 dark:border-[#3e3e42] rounded bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc]"
          />
        </div>
      </form>

      <template #footer>
        <button
          type="button"
          class="px-3 py-1.5 rounded border border-slate-300 dark:border-[#3e3e42] text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-100 dark:hover:bg-[#2a2d2e]"
          @click="isReviewModalOpen = false"
        >
          Cancel
        </button>
        <button
          type="button"
          :disabled="isSubmitting"
          class="px-4 py-1.5 rounded bg-slate-900 dark:bg-[#007acc] text-xs font-medium text-white hover:bg-slate-800 dark:hover:bg-[#1177bb] disabled:opacity-50"
          @click="handleConfirmReview"
        >
          <span v-if="isSubmitting">Saving…</span>
          <span v-else>Confirm Decision</span>
        </button>
      </template>
    </Modal>
  </div>
</template>
