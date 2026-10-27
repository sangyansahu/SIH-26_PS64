<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'
import {
  UploadCloud,
  FileSpreadsheet,
  Download,
  AlertCircle,
  CheckCircle2,
  XCircle,
  History,
  ArrowRight,
} from 'lucide-vue-next'

const file = ref<File | null>(null)
const isDragging = ref(false)
const isPreviewing = ref(false)
const isCommitting = ref(false)
const previewData = ref<any>(null)
const previewError = ref<string | null>(null)
const commitResult = ref<any>(null)
const importHistory = ref<any[]>([])

async function loadHistory() {
  try {
    const res = await apiClient.get('/imports/history')
    importHistory.value = res.data.batches || []
  } catch (err) {
    // Ignore
  }
}

onMounted(() => {
  loadHistory()
})

async function downloadTemplate() {
  try {
    const res = await apiClient.get('/imports/template', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/csv;charset=utf-8;' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'aicte_complaints_import_template.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Failed to download template:', err)
  }
}

function handleFileDrop(e: DragEvent) {
  isDragging.value = false
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    file.value = e.dataTransfer.files[0]
    previewFile()
  }
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    file.value = target.files[0]
    previewFile()
  }
}

async function previewFile() {
  if (!file.value) return
  isPreviewing.value = true
  previewError.value = null
  commitResult.value = null

  try {
    const text = await file.value.text()
    const res = await apiClient.post('/imports/preview', text, {
      headers: { 'Content-Type': 'text/csv' }
    })
    previewData.value = res.data
  } catch (err: any) {
    previewError.value = err.response?.data?.error || 'Failed to parse CSV file. Ensure valid format.'
    previewData.value = null
  } finally {
    isPreviewing.value = false
  }
}

async function commitValidRows() {
  if (!previewData.value?.valid_rows || previewData.value.valid_rows.length === 0) return
  isCommitting.value = true

  try {
    const res = await apiClient.post('/imports/commit', {
      filename: file.value?.name || 'import.csv',
      valid_rows: previewData.value.valid_rows,
    })
    commitResult.value = res.data
    previewData.value = null
    file.value = null
    await loadHistory()
  } catch (err: any) {
    previewError.value = err.response?.data?.error || 'Failed to commit import records.'
  } finally {
    isCommitting.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-slate-900 dark:text-[#d4d4d4]">
          Import Complaints
        </h1>
        <p class="text-xs text-slate-500 dark:text-[#989898] mt-0.5">
          Upload CSV files, preview validation errors, and import records
        </p>
      </div>

      <button
        type="button"
        class="inline-flex items-center gap-1.5 rounded border border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#2d2d2d] px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-[#cccccc] hover:bg-slate-50 dark:hover:bg-[#37373d] transition"
        @click="downloadTemplate"
      >
        <Download class="w-3.5 h-3.5 text-slate-500 dark:text-[#989898]" />
        Download Template
      </button>
    </div>

    <!-- Success Feedback Banner -->
    <div
      v-if="commitResult"
      class="rounded border border-emerald-300 dark:border-[#89d185]/30 bg-emerald-50 dark:bg-[#89d185]/10 p-3.5 flex items-center justify-between"
    >
      <div class="flex items-center gap-3">
        <CheckCircle2 class="w-5 h-5 text-emerald-600 dark:text-[#89d185]" />
        <div>
          <h2 class="text-xs font-semibold text-emerald-950 dark:text-[#89d185]">
            Import Completed
          </h2>
          <p class="text-xs text-emerald-800 dark:text-[#89d185]/80 mt-0.5">
            {{ commitResult.committed_count }} complaints imported.
          </p>
        </div>
      </div>
      <router-link
        to="/complaints"
        class="text-xs font-medium text-emerald-800 dark:text-[#89d185] underline hover:text-emerald-950 dark:hover:text-white"
      >
        View complaints →
      </router-link>
    </div>

    <!-- Upload Drag-and-Drop Area -->
    <div
      :class="[
        'rounded border-2 border-dashed p-8 text-center transition flex flex-col items-center justify-center',
        isDragging
          ? 'border-[#007acc] bg-[#007acc]/10'
          : 'border-slate-300 dark:border-[#3e3e42] bg-white dark:bg-[#252526] hover:border-slate-400 dark:hover:border-[#989898]'
      ]"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleFileDrop"
    >
      <div class="w-10 h-10 rounded-full bg-slate-100 dark:bg-[#1e1e1e] flex items-center justify-center text-slate-500 dark:text-[#989898] mb-3 border dark:border-[#2d2d2d]">
        <UploadCloud class="w-5 h-5" />
      </div>

      <h2 class="text-xs font-semibold text-slate-800 dark:text-[#cccccc]">
        Upload CSV File
      </h2>
      <p class="text-xs text-slate-500 dark:text-[#989898] mt-1 max-w-sm">
        Drag and drop your file here, or select browse to inspect rows before importing.
      </p>

      <label class="mt-4 inline-flex items-center gap-1.5 rounded bg-slate-900 dark:bg-[#007acc] px-4 py-1.5 text-xs font-medium text-white hover:bg-slate-800 dark:hover:bg-[#1177bb] cursor-pointer transition">
        <span>Browse File</span>
        <input
          type="file"
          accept=".csv"
          class="hidden"
          @change="handleFileSelect"
        />
      </label>

      <p v-if="file" class="mt-3 text-xs font-medium text-blue-600 dark:text-[#4fc1ff]">
        Selected file: {{ file.name }} ({{ (file.size / 1024).toFixed(1) }} KB)
      </p>
    </div>

    <!-- Error Banner -->
    <div
      v-if="previewError"
      class="rounded border border-red-200 dark:border-[#f48771]/30 bg-red-50 dark:bg-[#f48771]/15 p-3.5 text-xs text-red-800 dark:text-[#f48771] flex items-start gap-2"
    >
      <AlertCircle class="w-4 h-4 flex-shrink-0 mt-0.5" />
      <div>
        <p class="font-semibold">Import Error</p>
        <p class="mt-0.5">{{ previewError }}</p>
      </div>
    </div>

    <!-- Preview Results Section -->
    <div v-if="previewData" class="space-y-4">
      <!-- Summary Stats Header -->
      <div class="grid grid-cols-3 gap-4">
        <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] p-4">
          <p class="text-xs font-medium text-slate-400 dark:text-[#989898]">Total Rows</p>
          <p class="text-2xl font-semibold text-slate-900 dark:text-[#d4d4d4] mt-1">{{ previewData.total_rows }}</p>
        </div>

        <div class="rounded border border-emerald-200 dark:border-[#89d185]/30 bg-emerald-50/60 dark:bg-[#89d185]/10 p-4">
          <p class="text-xs font-medium text-emerald-800 dark:text-[#89d185]">Valid Rows</p>
          <p class="text-2xl font-semibold text-emerald-700 dark:text-[#89d185] mt-1">{{ previewData.valid_count }}</p>
        </div>

        <div class="rounded border border-red-200 dark:border-[#f48771]/30 bg-red-50/60 dark:bg-[#f48771]/10 p-4">
          <p class="text-xs font-medium text-red-800 dark:text-[#f48771]">Invalid Rows</p>
          <p class="text-2xl font-semibold text-red-700 dark:text-[#f48771] mt-1">{{ previewData.invalid_count }}</p>
        </div>
      </div>

      <!-- Action Button to Commit -->
      <div class="flex items-center justify-between bg-slate-900 dark:bg-[#252526] border dark:border-[#2d2d2d] text-white p-4 rounded">
        <div>
          <p class="text-xs font-semibold text-slate-100">Validation Summary</p>
          <p class="text-xs text-slate-400 mt-0.5">
            {{ previewData.valid_count }} rows verified and ready to be imported.
          </p>
        </div>

        <button
          type="button"
          :disabled="isCommitting || previewData.valid_count === 0"
          class="inline-flex items-center gap-1.5 rounded bg-emerald-600 hover:bg-emerald-700 dark:bg-[#007acc] dark:hover:bg-[#1177bb] px-4 py-1.5 text-xs font-medium text-white transition disabled:opacity-40"
          @click="commitValidRows"
        >
          <CheckCircle2 class="w-3.5 h-3.5" />
          <span v-if="isCommitting">Importing...</span>
          <span v-else>Import {{ previewData.valid_count }} records</span>
        </button>
      </div>

      <!-- Invalid Rows Table (if any) -->
      <div v-if="previewData.invalid_count > 0" class="rounded border border-red-200 dark:border-[#f48771]/30 bg-white dark:bg-[#252526] overflow-hidden">
        <div class="px-4 py-2.5 bg-red-50 dark:bg-[#f48771]/10 border-b border-red-100 dark:border-[#f48771]/20 flex items-center justify-between">
          <span class="text-xs font-semibold text-red-900 dark:text-[#f48771]">
            Rejected Rows ({{ previewData.invalid_count }})
          </span>
          <span class="text-xs text-red-600 dark:text-[#f48771]/80">These rows will be skipped</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 dark:bg-[#1e1e1e] border-b border-slate-200 dark:border-[#2d2d2d] text-xs text-slate-600 dark:text-[#cccccc] font-semibold">
              <tr>
                <th class="py-2 px-4">Row #</th>
                <th class="py-2 px-4">Institution</th>
                <th class="py-2 px-4">Subject</th>
                <th class="py-2 px-4">Validation Errors</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-[#2d2d2d]">
              <tr v-for="inv in previewData.invalid_rows" :key="inv.row_index" class="bg-red-50/20 dark:bg-[#f48771]/5">
                <td class="py-2 px-4 font-mono font-medium text-slate-700 dark:text-[#cccccc]">{{ inv.row_index }}</td>
                <td class="py-2 px-4 text-slate-800 dark:text-[#cccccc]">{{ inv.institution_code || inv.institution_name || 'Empty' }}</td>
                <td class="py-2 px-4 truncate max-w-xs text-slate-800 dark:text-[#cccccc]">{{ inv.subject || 'Empty' }}</td>
                <td class="py-2 px-4">
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="err in inv.errors"
                      :key="err"
                      class="rounded bg-red-100 dark:bg-[#f48771]/15 text-red-800 dark:text-[#f48771] border border-red-200 dark:border-[#f48771]/30 px-1.5 py-0.5 text-xs font-medium"
                    >
                      {{ err }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Valid Rows Preview Table -->
      <div v-if="previewData.valid_count > 0" class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] overflow-hidden">
        <div class="px-4 py-2.5 bg-slate-50 dark:bg-[#1e1e1e] border-b border-slate-200 dark:border-[#2d2d2d] flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-800 dark:text-[#cccccc]">
            Valid Rows ({{ previewData.valid_count }})
          </span>
          <span class="text-xs text-slate-500 dark:text-[#989898]">Ready to import</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 dark:bg-[#1e1e1e] border-b border-slate-200 dark:border-[#2d2d2d] text-xs text-slate-600 dark:text-[#cccccc] font-semibold">
              <tr>
                <th class="py-2 px-4">Institution</th>
                <th class="py-2 px-4">Bureau</th>
                <th class="py-2 px-4">Category</th>
                <th class="py-2 px-4">Priority</th>
                <th class="py-2 px-4">Subject</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-[#2d2d2d]">
              <tr v-for="v in previewData.valid_rows" :key="v.row_index" class="hover:bg-slate-50 dark:hover:bg-[#2a2d2e]">
                <td class="py-2 px-4 font-medium text-slate-900 dark:text-[#cccccc]">{{ v.institution_name }}</td>
                <td class="py-2 px-4 font-mono text-slate-800 dark:text-[#cccccc]">{{ v.bureau_code }}</td>
                <td class="py-2 px-4 text-slate-600 dark:text-[#989898]">{{ v.category }}</td>
                <td class="py-2 px-4 text-slate-800 dark:text-[#cccccc]">{{ v.priority }}</td>
                <td class="py-2 px-4 truncate max-w-sm text-slate-800 dark:text-[#cccccc]">{{ v.subject }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Past Import Batches History -->
    <div class="rounded border border-slate-200 dark:border-[#2d2d2d] bg-white dark:bg-[#252526] overflow-hidden">
      <div class="border-b border-slate-200 dark:border-[#2d2d2d] px-4 py-3">
        <h2 class="text-xs font-semibold text-slate-900 dark:text-[#cccccc] flex items-center gap-2">
          <History class="w-4 h-4 text-slate-500 dark:text-[#989898]" />
          Import History
        </h2>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-50 dark:bg-[#1e1e1e] border-b border-slate-200 dark:border-[#2d2d2d] text-xs font-semibold text-slate-600 dark:text-[#cccccc]">
            <tr>
              <th class="py-2.5 px-4">Batch ID</th>
              <th class="py-2.5 px-4">Filename</th>
              <th class="py-2.5 px-4">Imported</th>
              <th class="py-2.5 px-4">Failed</th>
              <th class="py-2.5 px-4">Operator</th>
              <th class="py-2.5 px-4">Timestamp</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-[#2d2d2d]">
            <tr v-for="b in importHistory" :key="b.id" class="hover:bg-slate-50 dark:hover:bg-[#2a2d2e]">
              <td class="py-2.5 px-4 font-mono font-medium text-slate-800 dark:text-[#cccccc]">#{{ b.id }}</td>
              <td class="py-2.5 px-4 font-medium text-slate-900 dark:text-[#d4d4d4]">{{ b.filename }}</td>
              <td class="py-2.5 px-4 text-emerald-700 dark:text-[#89d185] font-medium">{{ b.success_rows }} rows</td>
              <td class="py-2.5 px-4 text-red-600 dark:text-[#f48771] font-medium">{{ b.failed_rows }} rows</td>
              <td class="py-2.5 px-4 text-slate-600 dark:text-[#989898]">{{ b.created_by_name }}</td>
              <td class="py-2.5 px-4 text-slate-400 dark:text-[#989898] font-mono">{{ b.created_at?.slice(0, 16).replace('T', ' ') }}</td>
            </tr>

            <tr v-if="importHistory.length === 0">
              <td colspan="6" class="py-6 text-center text-xs text-slate-400 dark:text-[#989898]">
                No past import records found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
