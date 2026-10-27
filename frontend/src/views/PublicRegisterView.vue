<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  FilePlus2,
  ShieldCheck,
  Building2,
  UploadCloud,
  FileCheck2,
  X,
  AlertCircle,
  HelpCircle,
  CheckCircle2,
  Search,
  ArrowRight
} from 'lucide-vue-next'
import PublicNav from '@/components/PublicNav.vue'

const router = useRouter()

// Form Data
const complainantName = ref('')
const complainantEmail = ref('')
const complainantMobile = ref('')

// Institution Selection
const institutionMode = ref<'search' | 'manual'>('search')
const institutionSearchQuery = ref('')
const institutionSearchResults = ref<any[]>([])
const selectedInstitution = ref<any>(null)
const manualInstitutionName = ref('')
const manualInstitutionState = ref('')

// Grievance Details
const category = ref('Fee Overcharging / Capitation')
const subject = ref('')
const description = ref('')
const priority = ref('Medium')

// Supporting File
const selectedFile = ref<File | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

// State
const loading = ref(false)
const error = ref('')
const categories = ref<string[]>([
  'Fee Overcharging / Capitation',
  'Faculty Quality / Non-Payment',
  'Infrastructure Deficiencies',
  'Ragging Incident',
  'Approval / Accreditation Fraud',
  'Admission Irregularity',
  'General Administration'
])

const indianStates = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
  'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Delhi', 'Jammu & Kashmir', 'All India'
]

// Auto-adjust priority if category is Ragging
watch(category, (newCat) => {
  if (newCat.toLowerCase().includes('ragging')) {
    priority.value = 'Critical'
  } else if (priority.value === 'Critical') {
    priority.value = 'Medium'
  }
})

// Search institutions with debounce
let searchDebounceTimer: any = null
watch(institutionSearchQuery, (q) => {
  clearTimeout(searchDebounceTimer)
  if (!q || q.trim().length < 2) {
    institutionSearchResults.value = []
    return
  }
  searchDebounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`http://localhost:5000/api/v1/public/institutions?q=${encodeURIComponent(q.trim())}`)
      if (res.ok) {
        const data = await res.json()
        institutionSearchResults.value = data.institutions || []
      }
    } catch {
      // Ignore network errors in preview
    }
  }, 250)
})

function selectInstitution(inst: any) {
  selectedInstitution.value = inst
  institutionSearchQuery.value = inst.name
  institutionSearchResults.value = []
}

function clearSelectedInstitution() {
  selectedInstitution.value = null
  institutionSearchQuery.value = ''
  institutionSearchResults.value = []
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    if (file.size > 16 * 1024 * 1024) {
      error.value = 'File exceeds maximum upload limit of 16MB.'
      return
    }
    selectedFile.value = file
    error.value = ''
  }
}

function removeFile() {
  selectedFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function loadMeta() {
  try {
    const res = await fetch('http://localhost:5000/api/v1/public/meta')
    if (res.ok) {
      const data = await res.json()
      if (data.categories && data.categories.length) {
        categories.value = data.categories
      }
    }
  } catch {
    // Keep fallback list
  }
}

async function handleSubmit() {
  error.value = ''

  if (!complainantName.value.trim()) {
    error.value = 'Please enter complainant full name.'
    return
  }
  if (!complainantEmail.value.trim() || !complainantEmail.value.includes('@')) {
    error.value = 'Please enter a valid official or personal email address.'
    return
  }
  if (institutionMode.value === 'search' && !selectedInstitution.value && !institutionSearchQuery.value.trim()) {
    error.value = 'Please select or enter the concerned AICTE institution.'
    return
  }
  if (institutionMode.value === 'manual' && !manualInstitutionName.value.trim()) {
    error.value = 'Please enter the institution name.'
    return
  }
  if (!subject.value.trim()) {
    error.value = 'Please enter a concise subject line for your grievance.'
    return
  }
  if (!description.value.trim() || description.value.trim().length < 15) {
    error.value = 'Please provide detailed grievance description (minimum 15 characters).'
    return
  }

  loading.value = true

  try {
    const formData = new FormData()
    formData.append('complainant_name', complainantName.value.trim())
    formData.append('complainant_email', complainantEmail.value.trim())
    if (complainantMobile.value.trim()) {
      formData.append('complainant_mobile', complainantMobile.value.trim())
    }

    if (institutionMode.value === 'search' && selectedInstitution.value) {
      formData.append('institution_id', String(selectedInstitution.value.id))
      formData.append('institution_name', selectedInstitution.value.name)
    } else if (institutionMode.value === 'search' && institutionSearchQuery.value.trim()) {
      formData.append('institution_name', institutionSearchQuery.value.trim())
    } else {
      formData.append('institution_name', manualInstitutionName.value.trim())
      if (manualInstitutionState.value) {
        formData.append('institution_state', manualInstitutionState.value)
      }
    }

    formData.append('category', category.value)
    formData.append('subject', subject.value.trim())
    formData.append('description', description.value.trim())
    formData.append('priority', priority.value)

    if (selectedFile.value) {
      formData.append('file', selectedFile.value)
    }

    const res = await fetch('http://localhost:5000/api/v1/public/complaints', {
      method: 'POST',
      body: formData
    })

    const data = await res.json()

    if (!res.ok) {
      error.value = data.error || 'Failed to submit grievance. Please check your entries.'
      loading.value = false
      return
    }

    // Success: Navigate to confirmation page
    router.push({
      path: '/confirmation',
      query: {
        ticket: data.ticket_number,
        subject: data.complaint?.subject || subject.value,
        institution: data.complaint?.institution_name || selectedInstitution.value?.name || manualInstitutionName.value,
        category: data.complaint?.category || category.value,
        bureau: data.complaint?.bureau_name || 'Public Grievance Redressal Cell'
      },
      state: {
        ticket_number: data.ticket_number,
        subject: data.complaint?.subject || subject.value,
        institution_name: data.complaint?.institution_name || selectedInstitution.value?.name || manualInstitutionName.value,
        category: data.complaint?.category || category.value,
        bureau_name: data.complaint?.bureau_name || 'Public Grievance Redressal Cell'
      }
    })
  } catch (err: any) {
    error.value = 'Failed to connect to AICTE submission service. Please check your connection.'
    loading.value = false
  }
}

onMounted(() => {
  loadMeta()
})
</script>

<template>
  <div class="public-layout">
    <PublicNav />

    <main class="public-main">
      <div class="public-container">
        <!-- Header -->
        <div class="public-page-header">
          <div class="header-icon-title">
            <FilePlus2 :size="24" class="header-icon" />
            <h1>Register a grievance</h1>
          </div>
          <p class="public-page-subtitle">
            Submit a complaint concerning an AICTE-approved technical institution. A ticket number will be generated immediately to track status.
          </p>
        </div>

        <!-- Form Card -->
        <div class="public-form-card">
          <form @submit.prevent="handleSubmit">
            <!-- Section 1: Complainant Details -->
            <div class="form-section">
              <div class="section-title-row">
                <div>
                  <h2 class="form-section-heading">Complainant details</h2>
                  <p class="form-section-desc">Your contact information for verification and status updates.</p>
                </div>
              </div>

              <div class="form-grid-two">
                <div class="form-field">
                  <label for="complainant-name" class="field-label">
                    Full name <span class="required">*</span>
                  </label>
                  <input
                    id="complainant-name"
                    v-model="complainantName"
                    type="text"
                    class="public-input"
                    placeholder="Full name"
                    required
                  />
                </div>

                <div class="form-field">
                  <label for="complainant-email" class="field-label">
                    Email address <span class="required">*</span>
                  </label>
                  <input
                    id="complainant-email"
                    v-model="complainantEmail"
                    type="email"
                    class="public-input"
                    placeholder="email@example.com"
                    required
                  />
                </div>
              </div>

              <div class="form-field mt-3">
                <label for="complainant-mobile" class="field-label">
                  Mobile number <small class="text-quiet">(Optional)</small>
                </label>
                <input
                  id="complainant-mobile"
                  v-model="complainantMobile"
                  type="tel"
                  class="public-input"
                  placeholder="10-digit mobile number"
                />
              </div>
            </div>

            <!-- Divider -->
            <div class="section-divider" />

            <!-- Section 2: Target Institution -->
            <div class="form-section">
              <div class="section-title-row">
                <div>
                  <h2 class="form-section-heading">Target institution</h2>
                  <p class="form-section-desc">Select or enter the concerned AICTE institution.</p>
                </div>
              </div>

              <!-- Mode Switcher -->
              <div class="inst-mode-toggle">
                <button
                  type="button"
                  :class="['mode-btn', { 'mode-btn-active': institutionMode === 'search' }]"
                  @click="institutionMode = 'search'"
                >
                  <Search :size="14" /> Search Directory
                </button>
                <button
                  type="button"
                  :class="['mode-btn', { 'mode-btn-active': institutionMode === 'manual' }]"
                  @click="institutionMode = 'manual'"
                >
                  <Building2 :size="14" /> Enter Manually
                </button>
              </div>

              <!-- Search Mode -->
              <div v-if="institutionMode === 'search'" class="institution-search-wrap">
                <div class="search-input-box">
                  <Search :size="16" class="search-box-icon" />
                  <input
                    v-model="institutionSearchQuery"
                    type="text"
                    class="public-input"
                    placeholder="Search institution name or AICTE code"
                    :disabled="Boolean(selectedInstitution)"
                  />
                  <button
                    v-if="selectedInstitution"
                    type="button"
                    class="button button-quiet clear-inst-btn"
                    @click="clearSelectedInstitution"
                  >
                    <X :size="14" /> Change
                  </button>
                </div>

                <!-- Selected Institution Pill -->
                <div v-if="selectedInstitution" class="selected-inst-pill">
                  <CheckCircle2 :size="16" class="check-icon" />
                  <div class="selected-inst-copy">
                    <strong>{{ selectedInstitution.name }}</strong>
                    <small>Permanent ID: {{ selectedInstitution.institution_code }} · {{ selectedInstitution.state }}</small>
                  </div>
                </div>

                <!-- Autocomplete Dropdown -->
                <ul
                  v-if="!selectedInstitution && institutionSearchResults.length > 0"
                  class="inst-autocomplete-list"
                >
                  <li
                    v-for="inst in institutionSearchResults"
                    :key="inst.id"
                    class="inst-autocomplete-item"
                    @click="selectInstitution(inst)"
                  >
                    <strong>{{ inst.name }}</strong>
                    <small>{{ inst.state }} · AICTE Code: {{ inst.institution_code }}</small>
                  </li>
                </ul>
              </div>

              <!-- Manual Mode -->
              <div v-else class="form-grid-two">
                <div class="form-field">
                  <label for="manual-inst-name" class="field-label">
                    Institution name <span class="required">*</span>
                  </label>
                  <input
                    id="manual-inst-name"
                    v-model="manualInstitutionName"
                    type="text"
                    class="public-input"
                    placeholder="Institution name"
                  />
                </div>

                <div class="form-field">
                  <label for="manual-inst-state" class="field-label">State / Region</label>
                  <select id="manual-inst-state" v-model="manualInstitutionState" class="public-select">
                    <option value="">Select State</option>
                    <option v-for="state in indianStates" :key="state" :value="state">
                      {{ state }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Divider -->
            <div class="section-divider" />

            <!-- Section 3: Grievance Particulars -->
            <div class="form-section">
              <div class="section-title-row">
                <div>
                  <h2 class="form-section-heading">Grievance details</h2>
                  <p class="form-section-desc">Select the category and provide the facts of the matter.</p>
                </div>
              </div>

              <div class="form-grid-two">
                <div class="form-field">
                  <label for="grievance-category" class="field-label">
                    Category <span class="required">*</span>
                  </label>
                  <select id="grievance-category" v-model="category" class="public-select" required>
                    <option v-for="cat in categories" :key="cat" :value="cat">
                      {{ cat }}
                    </option>
                  </select>
                </div>

                <div class="form-field">
                  <label for="grievance-priority" class="field-label">
                    Urgency level
                  </label>
                  <select id="grievance-priority" v-model="priority" class="public-select">
                    <option value="Low">Low - Informational / non-urgent</option>
                    <option value="Medium">Medium - Standard inquiry</option>
                    <option value="High">High - Time-sensitive academic matter</option>
                    <option value="Critical">Critical - Urgent inquiry or ragging report</option>
                  </select>
                </div>
              </div>

              <div v-if="category.includes('Ragging')" class="ragging-alert">
                <AlertCircle :size="16" />
                <span>Ragging complaints receive critical priority and route directly to the Ragging Prevention Cell.</span>
              </div>

              <div class="form-field mt-3">
                <label for="grievance-subject" class="field-label">
                  Subject <span class="required">*</span>
                </label>
                <input
                  id="grievance-subject"
                  v-model="subject"
                  type="text"
                  class="public-input"
                  placeholder="Brief summary of the issue"
                  required
                />
              </div>

              <div class="form-field mt-3">
                <label for="grievance-description" class="field-label">
                  Detailed description <span class="required">*</span>
                </label>
                <textarea
                  id="grievance-description"
                  v-model="description"
                  rows="5"
                  class="public-textarea"
                  placeholder="State the facts, dates, fee details, affected cohorts, or institutional responses..."
                  required
                />
                <span class="char-count">{{ description.length }} characters</span>
              </div>
            </div>

            <!-- Divider -->
            <div class="section-divider" />

            <!-- Section 4: Supporting Evidence -->
            <div class="form-section">
              <div class="section-title-row">
                <div>
                  <h2 class="form-section-heading">Supporting documents (optional)</h2>
                  <p class="form-section-desc">Attach receipts, circulars, or correspondence (PDF, JPG, PNG, DOC, DOCX up to 16MB).</p>
                </div>
              </div>

              <div v-if="!selectedFile" class="file-drop-area">
                <input
                  ref="fileInputRef"
                  type="file"
                  class="file-input-hidden"
                  accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.txt"
                  @change="handleFileChange"
                />
                <div class="file-drop-content" @click="fileInputRef?.click()">
                  <UploadCloud :size="32" class="upload-icon" />
                  <strong>Select a document or image</strong>
                  <span>PDF, Word documents, or images up to 16MB</span>
                </div>
              </div>

              <div v-else class="file-selected-box">
                <div class="file-info-group">
                  <FileCheck2 :size="20" class="file-icon" />
                  <div>
                    <strong>{{ selectedFile.name }}</strong>
                    <small>{{ formatFileSize(selectedFile.size) }}</small>
                  </div>
                </div>
                <button type="button" class="button button-quiet" @click="removeFile">
                  <X :size="15" /> Remove
                </button>
              </div>
            </div>

            <!-- Error Banner -->
            <div v-if="error" class="public-error-card" role="alert">
              <AlertCircle :size="18" class="error-icon" />
              <div class="error-copy">
                <strong>Unable to register grievance</strong>
                <p>{{ error }}</p>
              </div>
            </div>

            <!-- Submit Button Bar -->
            <div class="form-submit-row">
              <div class="submit-note">
                <ShieldCheck :size="15" />
                <span>Submissions are logged directly into the AICTE case register.</span>
              </div>

              <button
                type="submit"
                class="button button-primary submit-btn"
                :disabled="loading"
              >
                <span v-if="loading">Registering Grievance…</span>
                <span v-else>Submit Grievance</span>
                <ArrowRight :size="16" />
              </button>
            </div>
          </form>
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
