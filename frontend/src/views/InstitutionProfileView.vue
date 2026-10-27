<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '@/api/client'
import StatusBadge from '@/components/StatusBadge.vue'
import PriorityBadge from '@/components/PriorityBadge.vue'
import type { Institution, Complaint, CaseLink } from '@/types'
import {
  ArrowLeft,
  Building2,
  MapPin,
  Globe,
  GitCompare,
  Clock,
  ArrowRight,
  ShieldAlert,
} from 'lucide-vue-next'

const route = useRoute()
const institutionId = computed(() => Number(route.params.id))

const loading = ref(true)
const institution = ref<Institution | null>(null)
const complaints = ref<Complaint[]>([])
const summary = ref<any>(null)
const potentialOverlaps = ref<CaseLink[]>([])

async function loadProfile() {
  loading.value = true
  try {
    const res = await apiClient.get(`/institutions/${institutionId.value}`)
    institution.value = res.data.institution
    complaints.value = res.data.complaints || []
    summary.value = res.data.summary || null
    potentialOverlaps.value = res.data.potential_overlaps || []
  } catch (err) {
    console.error('Failed to load institution profile:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<template>
  <div v-if="institution" class="space-y-6">
    <!-- Back Button -->
    <div>
      <router-link
        to="/institutions"
        class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-[#989898] hover:text-slate-800 dark:hover:text-[#cccccc] transition mb-3"
      >
        <ArrowLeft class="w-3.5 h-3.5" />
        Back to institutions
      </router-link>

      <!-- Title & Basic Info -->
      <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="rounded bg-slate-100 dark:bg-[#1e1e1e] px-2 py-0.5 text-xs font-mono font-medium text-slate-700 dark:text-[#cccccc] border border-slate-200 dark:border-[#2d2d2d]">
              AICTE ID: {{ institution.institution_code }}
            </span>
            <span class="rounded bg-blue-50 dark:bg-[#007acc]/15 text-blue-700 dark:text-[#4fc1ff] px-2.5 py-0.5 text-xs font-medium border border-blue-200 dark:border-[#007acc]/30">
              {{ institution.institution_type }}
            </span>
          </div>

          <h1 class="text-xl font-semibold tracking-tight text-slate-900 dark:text-[#d4d4d4] mt-2">
            {{ institution.name }}
          </h1>

          <div class="mt-2 flex flex-wrap items-center gap-4 text-xs text-slate-500 dark:text-[#989898]">
            <span class="flex items-center gap-1">
              <MapPin class="w-3.5 h-3.5 text-slate-400 dark:text-[#989898]" />
              {{ institution.address || `${institution.district}, ${institution.state}` }}
            </span>
            <span v-if="institution.website" class="flex items-center gap-1">
              <Globe class="w-3.5 h-3.5 text-slate-400 dark:text-[#989898]" />
              <a :href="institution.website" target="_blank" class="text-blue-600 dark:text-[#4fc1ff] hover:underline">
                {{ institution.website }}
              </a>
            </span>
          </div>

          <!-- Aliases -->
          <div v-if="institution.aliases && institution.aliases.length > 0" class="mt-3 flex items-center gap-2">
            <span class="text-xs font-medium text-slate-400 dark:text-[#989898]">Known aliases:</span>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="a in institution.aliases"
                :key="a"
                class="rounded bg-slate-100 dark:bg-[#1e1e1e] border border-slate-200 dark:border-[#2d2d2d] px-2 py-0.5 text-xs text-slate-700 dark:text-[#cccccc]"
              >
                {{ a }}
              </span>
            </div>
          </div>
        </div>

        <!-- Quick Summary Metrics -->
        <div class="flex items-center gap-5 border-t md:border-t-0 md:border-l border-slate-200 dark:border-[#2d2d2d] pt-4 md:pt-0 md:pl-6">
          <div class="text-center">
            <p class="text-xs font-medium text-slate-400 dark:text-[#989898]">Total</p>
            <p class="text-2xl font-semibold text-slate-900 dark:text-[#d4d4d4]">{{ summary?.total_complaints || 0 }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs font-medium text-slate-400 dark:text-[#989898]">Active</p>
            <p class="text-2xl font-semibold text-amber-600 dark:text-[#cca700]">{{ summary?.open_cases || 0 }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs font-medium text-slate-400 dark:text-[#989898]">Resolved</p>
            <p class="text-2xl font-semibold text-emerald-600 dark:text-[#89d185]">{{ summary?.disposed_cases || 0 }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs font-medium text-slate-400 dark:text-[#989898]">Overdue</p>
            <p class="text-2xl font-semibold text-red-600 dark:text-[#f48771]">{{ summary?.overdue_cases || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Cross-Bureau Distribution Alert -->
    <div
      v-if="potentialOverlaps.length > 0"
      class="rounded border border-amber-300 dark:border-[#cca700]/30 bg-amber-50 dark:bg-[#cca700]/10 p-3.5 flex items-center justify-between gap-4"
    >
      <div class="flex items-center gap-3">
        <GitCompare class="w-5 h-5 text-amber-700 dark:text-[#cca700] flex-shrink-0" />
        <div>
          <h2 class="text-xs font-semibold text-amber-950 dark:text-[#cca700]">
            {{ potentialOverlaps.length }} related overlap flags
          </h2>
          <p class="text-xs text-amber-900 dark:text-[#cca700]/80 mt-0.5">
            Complaints concerning this institution match records in other bureaus.
          </p>
        </div>
      </div>
      <router-link
        to="/overlaps"
        class="inline-flex items-center gap-1 text-xs font-medium text-amber-900 dark:text-[#cca700] bg-amber-200/80 dark:bg-[#2d2d2d] hover:bg-amber-200 dark:hover:bg-[#37373d] px-3 py-1.5 rounded transition border dark:border-[#3e3e42]"
      >
        Review Overlaps
        <ArrowRight class="w-3.5 h-3.5" />
      </router-link>
    </div>

    <!-- Bureau Workload Distribution for this College -->
    <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-4">
      <h2 class="text-xs font-semibold text-slate-800 dark:text-[#cccccc] border-b border-slate-100 dark:border-[#2d2d2d] pb-2.5">
        Complaints by Bureau
      </h2>
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-3">
        <div
          v-for="(count, code) in summary?.bureau_distribution"
          :key="code"
          class="p-2.5 rounded border border-slate-100 dark:border-[#2d2d2d] bg-slate-50 dark:bg-[#1e1e1e] text-center"
        >
          <span class="rounded bg-slate-900 dark:bg-[#2d2d2d] text-amber-400 dark:text-[#cca700] px-1.5 py-0.5 text-xs font-medium border dark:border-[#3e3e42]">
            {{ code }}
          </span>
          <p class="text-lg font-semibold text-slate-900 dark:text-[#d4d4d4] mt-1">{{ count }}</p>
          <p class="text-xs text-slate-500 dark:text-[#989898]">Filed</p>
        </div>
      </div>
    </div>

    <!-- Chronological Cross-Bureau Complaints Table -->
    <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] overflow-hidden">
      <div class="border-b border-slate-200 dark:border-[#2d2d2d] px-4 py-3">
        <h2 class="text-xs font-semibold text-slate-900 dark:text-[#cccccc]">
          Complaint History
        </h2>
        <p class="text-xs text-slate-500 dark:text-[#989898] mt-0.5">
          All registered complaints involving {{ institution.name }}
        </p>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-200 dark:border-[#2d2d2d] bg-slate-50 dark:bg-[#1e1e1e] text-xs font-semibold text-slate-600 dark:text-[#cccccc]">
              <th class="py-2.5 px-4">Case #</th>
              <th class="py-2.5 px-4">Subject & Description</th>
              <th class="py-2.5 px-4">Bureau</th>
              <th class="py-2.5 px-4">Category</th>
              <th class="py-2.5 px-4">Priority</th>
              <th class="py-2.5 px-4">Status</th>
              <th class="py-2.5 px-4">Received Date</th>
              <th class="py-2.5 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-[#2d2d2d] text-xs">
            <tr
              v-for="c in complaints"
              :key="c.id"
              class="hover:bg-slate-50/80 dark:hover:bg-[#2a2d2e] transition"
            >
              <td class="py-3 px-4 font-mono font-medium text-slate-900 dark:text-[#d4d4d4] whitespace-nowrap">
                <router-link :to="`/complaints/${c.id}`" class="text-blue-600 dark:text-[#4fc1ff] hover:underline">
                  {{ c.case_number }}
                </router-link>
              </td>

              <td class="py-3 px-4 max-w-sm">
                <p class="font-medium text-slate-900 dark:text-[#cccccc] line-clamp-1">{{ c.subject }}</p>
                <p class="text-xs text-slate-500 dark:text-[#989898] line-clamp-1 mt-0.5">{{ c.description }}</p>
              </td>

              <td class="py-3 px-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 dark:bg-[#2d2d2d] text-slate-700 dark:text-[#cccccc] border border-slate-200 dark:border-[#3e3e42]">
                  {{ c.current_bureau_code }}
                </span>
              </td>

              <td class="py-3 px-4 text-slate-600 dark:text-[#989898]">{{ c.category }}</td>

              <td class="py-3 px-4 whitespace-nowrap">
                <PriorityBadge :priority="c.priority" size="sm" />
              </td>

              <td class="py-3 px-4 whitespace-nowrap">
                <StatusBadge :status="c.status" size="sm" />
              </td>

              <td class="py-3 px-4 whitespace-nowrap text-slate-500 dark:text-[#989898]">
                {{ c.received_at ? c.received_at.slice(0, 10) : 'N/A' }}
              </td>

              <td class="py-3 px-4 text-right whitespace-nowrap">
                <router-link
                  :to="`/complaints/${c.id}`"
                  class="font-medium text-slate-700 dark:text-[#cccccc] hover:text-slate-900 dark:hover:text-white"
                >
                  View
                </router-link>
              </td>
            </tr>

            <tr v-if="complaints.length === 0">
              <td colspan="8" class="py-8 text-center text-xs text-slate-400 dark:text-[#989898]">
                No complaint records on file for this institution.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Loading Skeleton -->
  <div v-else-if="loading" class="space-y-6 animate-pulse">
    <div class="h-4 bg-slate-200 dark:bg-[#2d2d2d] rounded w-1/4"></div>
    <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-6 space-y-4">
      <div class="h-6 bg-slate-200 dark:bg-[#2d2d2d] rounded w-2/5"></div>
      <div class="h-4 bg-slate-200 dark:bg-[#2d2d2d] rounded w-3/5"></div>
      <div class="h-24 bg-slate-100 dark:bg-[#1e1e1e] rounded w-full"></div>
    </div>
  </div>

  <!-- Not Found State -->
  <div v-else class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-12 text-center space-y-4">
    <div class="inline-flex p-3 rounded-full bg-red-50 dark:bg-[#3b1214] text-red-600 dark:text-[#f48771]">
      <ShieldAlert class="w-6 h-6" />
    </div>
    <h2 class="text-base font-semibold text-slate-900 dark:text-white">Institution Profile Not Found</h2>
    <p class="text-xs text-slate-500 dark:text-[#989898] max-w-sm mx-auto [text-wrap:pretty]">
      The requested educational institution record could not be found in the AICTE directory.
    </p>
    <div>
      <router-link
        to="/institutions"
        class="inline-flex items-center gap-1.5 rounded-lg bg-[#c2410c] hover:bg-[#9a3412] px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all"
      >
        <ArrowLeft class="w-3.5 h-3.5" />
        Back to Directory
      </router-link>
    </div>
  </div>
</template>
