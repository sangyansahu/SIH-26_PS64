<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import apiClient from '@/api/client'
import type { Institution } from '@/types'
import {
  Building2,
  Search,
  Filter,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from 'lucide-vue-next'

const search = ref('')
const stateFilter = ref('')
const typeFilter = ref('')
const institutions = ref<Institution[]>([])
const total = ref(0)
const page = ref(1)
const perPage = ref(12)
const pages = ref(1)
const loading = ref(false)

const states = ref<string[]>([])
const institutionTypes = ref<string[]>([])

async function loadMetadata() {
  try {
    const res = await apiClient.get('/institutions/meta')
    states.value = res.data.states || []
    institutionTypes.value = res.data.institution_types || []
  } catch (err) {
    states.value = ['Delhi', 'Karnataka', 'Maharashtra', 'Odisha', 'Tamil Nadu', 'Uttar Pradesh']
    institutionTypes.value = ['Engineering & Technology', 'Management', 'Pharmacy', 'Polytechnic']
  }
}

async function fetchInstitutions() {
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      per_page: perPage.value,
    }
    if (search.value) params.search = search.value
    if (stateFilter.value) params.state = stateFilter.value
    if (typeFilter.value) params.institution_type = typeFilter.value

    const res = await apiClient.get('/institutions', { params })
    institutions.value = res.data.items || []
    total.value = res.data.total || 0
    pages.value = res.data.pages || 1
  } catch (err) {
    console.error('Failed to load institutions:', err)
  } finally {
    loading.value = false
  }
}

let searchTimer: any = null
watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchInstitutions()
  }, 300)
})

onMounted(() => {
  loadMetadata()
  fetchInstitutions()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-slate-900 dark:text-[#d4d4d4]">
          Institutions
        </h1>
        <p class="text-xs text-slate-500 dark:text-[#989898] mt-0.5">
          Browse institutions, view aliases, and inspect complaint records across bureaus
        </p>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-3.5">
      <!-- Search -->
      <div class="relative">
        <Search class="w-4 h-4 text-slate-400 dark:text-[#989898] absolute left-3 top-2.5 pointer-events-none" />
        <input
          v-model="search"
          type="text"
          aria-label="Search institutions"
          placeholder="Search by name, permanent ID, or alias..."
          class="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc] placeholder-slate-400 dark:placeholder-[#aaaaaa] transition"
        />
      </div>

      <!-- State Filter -->
      <div>
        <select
          v-model="stateFilter"
          aria-label="Filter by state"
          class="w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] transition bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
          @change="page = 1; fetchInstitutions()"
        >
          <option value="">All States and Union Territories</option>
          <option v-for="st in states" :key="st" :value="st">
            {{ st }}
          </option>
        </select>
      </div>

      <!-- Type Filter -->
      <div>
        <select
          v-model="typeFilter"
          aria-label="Filter by type"
          class="w-full px-3 py-1.5 text-xs border border-slate-300 dark:border-[#3e3e42] rounded focus:ring-1 focus:ring-[#007acc] focus:border-[#007acc] transition bg-white dark:bg-[#3c3c3c] text-slate-900 dark:text-[#cccccc]"
          @change="page = 1; fetchInstitutions()"
        >
          <option value="">All Institution Types</option>
          <option v-for="t in institutionTypes" :key="t" :value="t">
            {{ t }}
          </option>
        </select>
      </div>
    </div>

    <!-- Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="inst in institutions"
        :key="inst.id"
        class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-4 hover:border-slate-300 dark:hover:border-[#3e3e42] transition flex flex-col justify-between"
      >
        <div>
          <div class="flex items-start justify-between gap-2">
            <span class="rounded bg-slate-100 dark:bg-[#1e1e1e] px-2 py-0.5 text-xs font-mono font-medium text-slate-700 dark:text-[#cccccc] border border-slate-200 dark:border-[#2d2d2d]">
              ID: {{ inst.institution_code }}
            </span>
            <span class="text-xs font-medium text-slate-500 dark:text-[#989898]">
              {{ inst.institution_type }}
            </span>
          </div>

          <h2 class="font-medium text-sm text-slate-900 dark:text-[#d4d4d4] mt-2 line-clamp-2 [text-wrap:balance]">
            {{ inst.name }}
          </h2>

          <p class="text-xs text-slate-500 dark:text-[#989898] mt-1">
            {{ inst.district ? `${inst.district}, ` : '' }}{{ inst.state }}
          </p>

          <!-- Associated aliases -->
          <div v-if="inst.aliases && inst.aliases.length > 0" class="mt-2.5 flex flex-wrap gap-1">
            <span
              v-for="a in inst.aliases"
              :key="a"
              class="rounded bg-slate-50 dark:bg-[#1e1e1e] border border-slate-200 dark:border-[#2d2d2d] px-1.5 py-0.5 text-xs text-slate-600 dark:text-[#989898]"
            >
              {{ a }}
            </span>
          </div>
        </div>

        <div class="mt-5 pt-3 border-t border-slate-100 dark:border-[#2d2d2d] flex items-center justify-between">
          <div class="text-xs text-slate-600 dark:text-[#989898]">
            <span class="font-medium text-slate-900 dark:text-[#cccccc]">{{ inst.total_complaints || 0 }}</span> total
            · <span class="font-medium text-[#cca700]">{{ inst.open_complaints || 0 }}</span> active
            · <span class="font-medium text-[#89d185]">{{ inst.disposed_complaints || 0 }}</span> resolved
          </div>

          <router-link
            :to="`/institutions/${inst.id}`"
            class="inline-flex items-center gap-1 text-xs font-medium text-blue-600 dark:text-[#4fc1ff] hover:underline"
          >
            Profile
            <ArrowRight class="w-3.5 h-3.5" />
          </router-link>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="institutions.length === 0 && !loading" class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-8 text-center text-xs text-slate-500 dark:text-[#989898]">
      No institutions match the current search filters.
    </div>

    <!-- Pagination -->
    <div v-if="pages > 1" class="flex items-center justify-between border-t border-slate-200 dark:border-[#2d2d2d] pt-4">
      <div class="text-xs text-slate-500 dark:text-[#989898]">
        Page {{ page }} of {{ pages }} ({{ total }} institutions)
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          :disabled="page <= 1"
          class="rounded border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-2.5 py-1 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-50 dark:hover:bg-[#37373d] disabled:opacity-40"
          @click="page--; fetchInstitutions()"
        >
          Previous
        </button>
        <button
          type="button"
          :disabled="page >= pages"
          class="rounded border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-2.5 py-1 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-50 dark:hover:bg-[#37373d] disabled:opacity-40"
          @click="page++; fetchInstitutions()"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>
