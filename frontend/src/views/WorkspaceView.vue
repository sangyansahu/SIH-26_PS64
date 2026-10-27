<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import type { Complaint, Institution, CaseLink, NotificationItem, KPIs } from '@/types'
import {
  Activity, AlertCircle, ArrowRight, ArrowUpRight, Building2,
  CalendarClock, Check, CheckCheck, ChevronDown, ChevronLeft, ChevronRight,
  CircleAlert, Clock3, Download, FileSearch, FileSpreadsheet, Filter, CheckCircle2,
  GitCompare, Layers3, ListFilter, LoaderCircle, Plus, RefreshCw, Search,
  ShieldCheck, Upload, X, ClipboardCheck, FileText, Database,
  KeyRound, UserPlus, Sliders, Trash2,
} from 'lucide-vue-next'


const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()

type Row = Record<string, any>

const isoDaysAgo = (days: number) => {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString()
}
const isoDaysFromNow = (days: number) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  return date.toISOString()
}

const sampleInstitutions: Row[] = [
  { id: 1, institution_code: 'AICTE-AP-0412', name: 'Apex Institute of Technology & Management', aliases: ['Apex Institute'], institution_type: 'Engineering & Technology', state: 'Madhya Pradesh', district: 'Indore', address: 'AB Road, Indore', total_complaints: 3, open_complaints: 3, disposed_complaints: 0, escalated_complaints: 0, bureaus_involved: ['PGRC', 'AB', 'PAPB'] },
  { id: 2, institution_code: 'AICTE-MH-1018', name: 'Western Valley College of Engineering', aliases: ['WVCE'], institution_type: 'Engineering & Technology', state: 'Maharashtra', district: 'Pune', total_complaints: 2, open_complaints: 1, disposed_complaints: 1, escalated_complaints: 0, bureaus_involved: ['AB', 'FAB'] },
  { id: 3, institution_code: 'AICTE-KA-0884', name: 'Deccan School of Applied Sciences', aliases: ['Deccan SAS'], institution_type: 'Applied Sciences', state: 'Karnataka', district: 'Mysuru', total_complaints: 1, open_complaints: 1, disposed_complaints: 0, escalated_complaints: 0, bureaus_involved: ['PGRC'] },
  { id: 4, institution_code: 'AICTE-RJ-0226', name: 'Rajasthan Institute of Technical Studies', aliases: ['RITS'], institution_type: 'Engineering & Technology', state: 'Rajasthan', district: 'Jaipur', total_complaints: 1, open_complaints: 1, disposed_complaints: 0, escalated_complaints: 1, bureaus_involved: ['RPC'] },
  { id: 5, institution_code: 'AICTE-TN-0675', name: 'Southern Polytechnic & Research Centre', aliases: ['SPRC'], institution_type: 'Polytechnic', state: 'Tamil Nadu', district: 'Coimbatore', total_complaints: 0, open_complaints: 0, disposed_complaints: 0, escalated_complaints: 0, bureaus_involved: [] },
  { id: 6, institution_code: 'AICTE-UP-0703', name: 'Northgate College of Engineering', aliases: ['Northgate'], institution_type: 'Engineering & Technology', state: 'Uttar Pradesh', district: 'Lucknow', total_complaints: 1, open_complaints: 1, disposed_complaints: 0, escalated_complaints: 0, bureaus_involved: ['AB'] },
]

const sampleComplaints: Row[] = [
  { id: 101, case_number: 'AICTE-26-PGRC-0101', external_reference: 'CPGRAMS/2026/004189', institution_id: 1, institution_name: sampleInstitutions[0].name, institution_code: sampleInstitutions[0].institution_code, institution_state: 'Madhya Pradesh', category: 'Fee irregularity', subject: 'Reported capitation fee collection during admission', description: 'The complainant reports an additional payment being requested outside the published fee schedule.', receiving_bureau_id: 1, receiving_bureau_code: 'PGRC', receiving_bureau_name: 'Public Grievance Redressal Cell', current_bureau_id: 1, current_bureau_code: 'PGRC', current_bureau_name: 'Public Grievance Redressal Cell', assigned_user_id: 2, assigned_officer_name: 'Ananya Rao', priority: 'Critical', status: 'Action Required', is_overdue: true, received_at: isoDaysAgo(18), due_at: isoDaysAgo(2), last_action_at: isoDaysAgo(5), created_at: isoDaysAgo(18) },
  { id: 102, case_number: 'AICTE-26-AB-0102', external_reference: 'CPGRAMS/2026/004189', institution_id: 1, institution_name: sampleInstitutions[0].name, institution_code: sampleInstitutions[0].institution_code, institution_state: 'Madhya Pradesh', category: 'Admission irregularity', subject: 'Review of admission-related fee complaint', description: 'Review requested on the institution fee schedule and additional admission charges reported by applicants.', receiving_bureau_id: 2, receiving_bureau_code: 'AB', receiving_bureau_name: 'Approval Bureau', current_bureau_id: 2, current_bureau_code: 'AB', current_bureau_name: 'Approval Bureau', assigned_user_id: 3, assigned_officer_name: 'Vikram Nair', priority: 'High', status: 'Under Review', is_overdue: false, received_at: isoDaysAgo(14), due_at: isoDaysFromNow(3), last_action_at: isoDaysAgo(1), created_at: isoDaysAgo(14) },
  { id: 103, case_number: 'AICTE-26-PAPB-0103', institution_id: 1, institution_name: sampleInstitutions[0].name, institution_code: sampleInstitutions[0].institution_code, institution_state: 'Madhya Pradesh', category: 'Faculty compliance', subject: 'Faculty qualification records need verification', description: 'Submitted faculty qualification documents appear incomplete and require a bureau-level review.', receiving_bureau_id: 3, receiving_bureau_code: 'PAPB', receiving_bureau_name: 'Policy & Academic Planning Bureau', current_bureau_id: 3, current_bureau_code: 'PAPB', current_bureau_name: 'Policy & Academic Planning Bureau', assigned_user_id: 4, assigned_officer_name: 'Meera Shah', priority: 'Medium', status: 'Awaiting Response', is_overdue: false, received_at: isoDaysAgo(9), due_at: isoDaysFromNow(6), last_action_at: isoDaysAgo(2), created_at: isoDaysAgo(9) },
  { id: 104, case_number: 'AICTE-26-RPC-0104', institution_id: 4, institution_name: sampleInstitutions[3].name, institution_code: sampleInstitutions[3].institution_code, institution_state: 'Rajasthan', category: 'Student safety', subject: 'Follow-up required on student safety report', description: 'A follow-up report requested from the institution has not yet been received.', receiving_bureau_id: 4, receiving_bureau_code: 'RPC', receiving_bureau_name: 'Ragging Prevention Cell', current_bureau_id: 4, current_bureau_code: 'RPC', current_bureau_name: 'Ragging Prevention Cell', assigned_user_id: 5, assigned_officer_name: 'Kunal Mehta', priority: 'High', status: 'Escalated', is_overdue: true, received_at: isoDaysAgo(23), due_at: isoDaysAgo(7), last_action_at: isoDaysAgo(8), created_at: isoDaysAgo(23) },
  { id: 105, case_number: 'AICTE-26-FAB-0105', institution_id: 2, institution_name: sampleInstitutions[1].name, institution_code: sampleInstitutions[1].institution_code, institution_state: 'Maharashtra', category: 'Financial records', subject: 'Scholarship disbursement reconciliation', description: 'Request to reconcile the recorded disbursement and the payment schedule supplied by the institution.', receiving_bureau_id: 5, receiving_bureau_code: 'FAB', receiving_bureau_name: 'Finance & Accounts Bureau', current_bureau_id: 5, current_bureau_code: 'FAB', current_bureau_name: 'Finance & Accounts Bureau', assigned_user_id: 6, assigned_officer_name: 'Sana Khan', priority: 'Medium', status: 'Under Review', is_overdue: false, received_at: isoDaysAgo(7), due_at: isoDaysFromNow(8), last_action_at: isoDaysAgo(2), created_at: isoDaysAgo(7) },
  { id: 106, case_number: 'AICTE-26-AB-0106', institution_id: 2, institution_name: sampleInstitutions[1].name, institution_code: sampleInstitutions[1].institution_code, institution_state: 'Maharashtra', category: 'Infrastructure', subject: 'Laboratory inventory records submitted', description: 'The institution submitted updated records in response to an earlier infrastructure query.', receiving_bureau_id: 2, receiving_bureau_code: 'AB', receiving_bureau_name: 'Approval Bureau', current_bureau_id: 2, current_bureau_code: 'AB', current_bureau_name: 'Approval Bureau', assigned_user_id: 3, assigned_officer_name: 'Vikram Nair', priority: 'Low', status: 'Disposed', is_overdue: false, received_at: isoDaysAgo(32), due_at: isoDaysAgo(12), last_action_at: isoDaysAgo(11), disposed_at: isoDaysAgo(11), created_at: isoDaysAgo(32) },
  { id: 107, case_number: 'AICTE-26-PGRC-0107', institution_id: 3, institution_name: sampleInstitutions[2].name, institution_code: sampleInstitutions[2].institution_code, institution_state: 'Karnataka', category: 'Faculty grievance', subject: 'Pending faculty salary clarification', description: 'A faculty member requests clarification about the timing of a salary payment.', receiving_bureau_id: 1, receiving_bureau_code: 'PGRC', receiving_bureau_name: 'Public Grievance Redressal Cell', current_bureau_id: 1, current_bureau_code: 'PGRC', current_bureau_name: 'Public Grievance Redressal Cell', assigned_user_id: 2, assigned_officer_name: 'Ananya Rao', priority: 'Medium', status: 'Received', is_overdue: false, received_at: isoDaysAgo(2), due_at: isoDaysFromNow(13), last_action_at: null, created_at: isoDaysAgo(2) },
  { id: 108, case_number: 'AICTE-26-AB-0108', institution_id: 6, institution_name: sampleInstitutions[5].name, institution_code: sampleInstitutions[5].institution_code, institution_state: 'Uttar Pradesh', category: 'Approval compliance', subject: 'Extension of approval documentation', description: 'A set of documents is awaiting administrative review before a decision can be recorded.', receiving_bureau_id: 2, receiving_bureau_code: 'AB', receiving_bureau_name: 'Approval Bureau', current_bureau_id: 2, current_bureau_code: 'AB', current_bureau_name: 'Approval Bureau', assigned_user_id: 3, assigned_officer_name: 'Vikram Nair', priority: 'High', status: 'Under Review', is_overdue: false, received_at: isoDaysAgo(5), due_at: isoDaysFromNow(2), last_action_at: isoDaysAgo(1), created_at: isoDaysAgo(5) },
]

const sampleOverlaps: Row[] = [
  { id: 501, complaint_id_a: 101, complaint_id_b: 102, relationship_type: 'potential_overlap', match_score: 0.93, match_method: 'Identifier + text similarity', match_reason: 'Both records reference the same institution and external complaint reference. The descriptions concern admission-related fees.', review_status: 'pending', created_at: isoDaysAgo(1), case_a: { id: 101, case_number: sampleComplaints[0].case_number, subject: sampleComplaints[0].subject, description: sampleComplaints[0].description, category: sampleComplaints[0].category, status: sampleComplaints[0].status, priority: sampleComplaints[0].priority, bureau_code: 'PGRC', institution_name: sampleInstitutions[0].name, institution_code: sampleInstitutions[0].institution_code }, case_b: { id: 102, case_number: sampleComplaints[1].case_number, subject: sampleComplaints[1].subject, description: sampleComplaints[1].description, category: sampleComplaints[1].category, status: sampleComplaints[1].status, priority: sampleComplaints[1].priority, bureau_code: 'AB', institution_name: sampleInstitutions[0].name, institution_code: sampleInstitutions[0].institution_code } },
  { id: 502, complaint_id_a: 105, complaint_id_b: 106, relationship_type: 'potential_overlap', match_score: 0.54, match_method: 'Institution identity match', match_reason: 'Both records reference the same institution, but their subjects differ. This may be a shared-entity match rather than related casework.', review_status: 'pending', created_at: isoDaysAgo(3), case_a: { id: 105, case_number: sampleComplaints[4].case_number, subject: sampleComplaints[4].subject, description: sampleComplaints[4].description, category: sampleComplaints[4].category, status: sampleComplaints[4].status, priority: sampleComplaints[4].priority, bureau_code: 'FAB', institution_name: sampleInstitutions[1].name, institution_code: sampleInstitutions[1].institution_code }, case_b: { id: 106, case_number: sampleComplaints[5].case_number, subject: sampleComplaints[5].subject, description: sampleComplaints[5].description, category: sampleComplaints[5].category, status: sampleComplaints[5].status, priority: sampleComplaints[5].priority, bureau_code: 'AB', institution_name: sampleInstitutions[1].name, institution_code: sampleInstitutions[1].institution_code } },
  { id: 503, complaint_id_a: 101, complaint_id_b: 103, relationship_type: 'potential_overlap', match_score: 0.42, match_method: 'Institution identity match', match_reason: 'The records belong to the same institution, but their subjects concern different matters (admission fees and faculty qualification records). Review whether any coordination is needed; do not assume they are duplicates.', review_status: 'pending', created_at: isoDaysAgo(4), case_a: { id: 101, case_number: sampleComplaints[0].case_number, subject: sampleComplaints[0].subject, description: sampleComplaints[0].description, category: sampleComplaints[0].category, status: sampleComplaints[0].status, priority: sampleComplaints[0].priority, bureau_code: 'PGRC', institution_name: sampleInstitutions[0].name, institution_code: sampleInstitutions[0].institution_code }, case_b: { id: 103, case_number: sampleComplaints[2].case_number, subject: sampleComplaints[2].subject, description: sampleComplaints[2].description, category: sampleComplaints[2].category, status: sampleComplaints[2].status, priority: sampleComplaints[2].priority, bureau_code: 'PAPB', institution_name: sampleInstitutions[0].name, institution_code: sampleInstitutions[0].institution_code } },
]

const sampleNotifications: Row[] = [
  { id: 701, notification_type: 'overlap', title: 'Potential overlap needs review', message: `${sampleComplaints[0].case_number} may be related to ${sampleComplaints[1].case_number}.`, related_complaint_id: 101, is_read: false, created_at: isoDaysAgo(1) },
  { id: 702, notification_type: 'deadline', title: 'Case is past due', message: `${sampleComplaints[3].case_number} is 7 days past its due date.`, related_complaint_id: 104, is_read: false, created_at: isoDaysAgo(1) },
  { id: 703, notification_type: 'assignment', title: 'New case entered the register', message: `${sampleComplaints[6].case_number} was received and is awaiting initial review.`, related_complaint_id: 107, is_read: true, created_at: isoDaysAgo(2) },
]

function readStored<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) as T : structuredClone(fallback)
  } catch {
    return structuredClone(fallback)
  }
}
function saveStored(key: string, value: unknown) {
  try { localStorage.setItem(key, JSON.stringify(value)) } catch { /* storage can be disabled */ }
}

const complaints = ref<Row[]>(readStored('casework_demo_complaints', sampleComplaints))
const institutions = ref<Row[]>(readStored('casework_demo_institutions', sampleInstitutions))
const overlaps = ref<Row[]>(readStored('casework_demo_overlaps', sampleOverlaps))
const notifications = ref<Row[]>(readStored('casework_demo_notifications', sampleNotifications))
const bureaus = ref<Row[]>([
  { id: 1, code: 'PGRC', name: 'Public Grievance Redressal Cell', description: 'Public, student and faculty grievances' },
  { id: 2, code: 'AB', name: 'Approval Bureau', description: 'Approval and compliance reviews' },
  { id: 3, code: 'PAPB', name: 'Policy & Academic Planning Bureau', description: 'Academic policy and faculty standards' },
  { id: 4, code: 'RPC', name: 'Ragging Prevention Cell', description: 'Student safety and prevention' },
  { id: 5, code: 'FAB', name: 'Finance & Accounts Bureau', description: 'Financial compliance and accounts' },
])
const kpis = ref<Row>({})
const loading = ref(false)
const forceDemoMode = ref(typeof sessionStorage !== 'undefined' && sessionStorage.getItem('casework_demo_mode') === '1')
const refreshing = ref(false)
const newComplaintOpen = ref(false)
const activeFilter = ref('All cases')
const statusFilter = ref('All statuses')
const bureauFilter = ref('All Bureaus')
const overlapFilter = ref('pending')
const institutionTypeFilter = ref('All types')
const notificationFilter = ref('all')
const pageNumber = ref(1)
const pageSize = 8
const selectedOverlap = ref<Row | null>(null)
const isReviewing = ref(false)
const selectedFile = ref<File | null>(null)
const importPreview = ref<Row | null>(null)
const importHistory = ref<Row[]>([])
const adminUsers = ref<Row[]>([])
const auditLogs = ref<Row[]>([])
const systemStatus = ref<Row | null>(null)
const adminIndustries = ref<Row[]>([])
const adminSettings = ref<Row>({
  categories: [
    "Fee Overcharging / Capitation",
    "Faculty Quality / Non-Payment",
    "Infrastructure Deficiencies",
    "Ragging Incident",
    "Approval / Accreditation Fraud",
    "Admission Irregularity",
    "General Administration"
  ],
  sla_days: { Critical: 7, High: 15, Medium: 30, Low: 45 }
})
const newCategoryInput = ref('')
const isCreateIndustryOpen = ref(false)
const newIndustryUser = reactive({
  name: '',
  email: '',
  password: '',
  bureau_id: '1',
  designation: 'Departmental Caseworker',
  role: 'INDUSTRY'
})
const isResetPasswordOpen = ref(false)
const selectedResetUser = ref<Row | null>(null)
const newPasswordInput = ref('')
const userRoleFilter = ref('ALL')
const toastLocal = (message: string, kind: 'success' | 'error' | 'info' = 'success') => ui.toast(message, kind)

// Case Action & Coordination Modals
const isNextActionOpen = ref(false)
const nextActionText = ref('')
const nextActionDueDate = ref('')
const nextActionAssignee = ref('')

const isCoordinationNoteOpen = ref(false)
const coordinationNoteText = ref('')

const isRequestInfoOpen = ref(false)
const requestInfoQuery = ref('')

const isTransferOpen = ref(false)
const transferBureauId = ref('1')
const transferReason = ref('')

const isEscalateOpen = ref(false)
const escalateReason = ref('')

const isLinkCaseOpen = ref(false)
const linkCaseNumber = ref('')
const linkCaseNotes = ref('')

const isReassignOpen = ref(false)
const reassignOfficerId = ref('')

const overlapReviewRemarks = ref('')

const newForm = reactive({
  subject: '',
  description: '',
  institution_id: '1',
  bureau_id: '1',
  category: 'General administration',
  priority: 'Medium',
  due_at: isoDaysFromNow(14).slice(0, 10),
})

const page = computed(() => {
  const path = route.path
  if (path === '/') return 'dashboard'
  if (path === '/complaints') return 'complaints'
  if (path.startsWith('/complaints/')) return 'detail'
  if (path === '/institutions') return 'institutions'
  if (path.startsWith('/institutions/')) return 'institution'
  if (path === '/overlaps') return 'overlaps'
  if (path === '/reports') return 'reports'
  if (path === '/notifications') return 'notifications'
  if (path === '/imports') return 'imports'
  if (path === '/admin') return 'admin'
  return 'dashboard'
})
const pageHeading = computed(() => ({
  dashboard: 'Overview', complaints: 'Complaints', detail: 'Complaint details', institutions: 'Institutions', institution: 'Institution profile', overlaps: 'Overlap review', reports: 'Reports', notifications: 'Notifications', imports: 'Data imports', admin: 'Administration',
}[page.value] || 'Overview'))
const pageSubheading = computed(() => ({
  dashboard: 'Open casework, deadlines and pending reviews.',
  complaints: 'Search and manage institution complaints.',
  detail: '',
  institutions: 'Directory of technical institutions and associated cases.',
  institution: 'Case history and regulatory profile.',
  overlaps: 'Potential duplicate and related cases for officer verification.',
  reports: 'Workload distribution and case ageing metrics.',
  notifications: 'Alerts for assignments, deadlines and transfers.',
  imports: 'Validate and import complaint records from CSV.',
  admin: 'User accounts, audit logs and system status.',
}[page.value] || ''))
const currentComplaintId = computed(() => Number(route.params.id || 0))
const currentInstitutionId = computed(() => Number(route.params.id || 0))
const currentComplaint = computed(() => complaints.value.find((item) => Number(item.id) === currentComplaintId.value) || null)
const currentInstitution = computed(() => institutions.value.find((item) => Number(item.id) === currentInstitutionId.value) || null)
const globalQuery = computed(() => ui.globalSearch.trim().toLowerCase())
const openComplaints = computed(() => complaints.value.filter((item) => !['Disposed', 'Closed'].includes(item.status)))
const overdueComplaints = computed(() => complaints.value.filter((item) => item.is_overdue || (item.due_at && new Date(item.due_at).getTime() < Date.now() && !['Disposed', 'Closed'].includes(item.status))))
const pendingOverlaps = computed(() => overlaps.value.filter((item) => (item.review_status || 'pending') === 'pending'))
const openCount = computed(() => kpis.value.open_cases ?? openComplaints.value.length)
const disposedCount = computed(() => kpis.value.disposed_cases ?? complaints.value.filter((item) => ['Disposed', 'Closed'].includes(item.status)).length)
const actionCount = computed(() => kpis.value.action_required ?? complaints.value.filter((item) => item.status === 'Action Required').length)
const overdueCount = computed(() => kpis.value.overdue_cases ?? overdueComplaints.value.length)
const totalCount = computed(() => kpis.value.total_complaints ?? complaints.value.length)
const unreadCount = computed(() => notifications.value.filter((item) => !item.is_read && !item.read_at).length)

// Six Specific Industry Dashboard Categories
const newComplaintsCount = computed(() => complaints.value.filter((item) => ['New', 'Received'].includes(item.status)).length)
const assignedComplaintsCount = computed(() => complaints.value.filter((item) => Boolean(item.assigned_user_id || item.assigned_officer_name)).length)
const inProgressComplaintsCount = computed(() => complaints.value.filter((item) => ['Under Review', 'Action Required', 'Awaiting Response', 'Escalated'].includes(item.status)).length)
const resolvedCount = computed(() => complaints.value.filter((item) => ['Disposed', 'Closed', 'Resolved'].includes(item.status)).length)
const overlappingCount = computed(() => pendingOverlaps.value.length)

const filteredAdminUsers = computed(() => {
  let list = adminUsers.value
  if (userRoleFilter.value === 'INDUSTRY') {
    list = list.filter((u) => ['INDUSTRY', 'OFFICER', 'SENIOR_AUTHORITY'].includes((u.role || '').toUpperCase()))
  } else if (userRoleFilter.value === 'SYSTEM_ADMIN') {
    list = list.filter((u) => ['SYSTEM_ADMIN', 'ADMIN'].includes((u.role || '').toUpperCase()))
  } else if (userRoleFilter.value === 'USER') {
    list = list.filter((u) => ['USER', 'CITIZEN'].includes((u.role || '').toUpperCase()))
  }
  return list
})

const recentComplaints = computed(() => [...complaints.value].sort((a, b) => new Date(b.created_at || b.received_at).getTime() - new Date(a.created_at || a.received_at).getTime()).slice(0, 6))
const visibleComplaints = computed(() => {
  let rows = [...complaints.value]
  if (globalQuery.value) rows = rows.filter((item) => [item.case_number, item.subject, item.institution_name, item.institution_code, item.category, item.current_bureau_name].some((value) => String(value || '').toLowerCase().includes(globalQuery.value)))
  if (statusFilter.value !== 'All statuses') rows = rows.filter((item) => item.status === statusFilter.value)
  if (bureauFilter.value !== 'All Bureaus') rows = rows.filter((item) => (item.current_bureau_code || item.receiving_bureau_code) === bureauFilter.value)
  if (activeFilter.value === 'Open cases') rows = rows.filter((item) => !['Disposed', 'Closed'].includes(item.status))
  if (activeFilter.value === 'Overdue') rows = rows.filter((item) => item.is_overdue || (item.due_at && new Date(item.due_at).getTime() < Date.now() && !['Disposed', 'Closed'].includes(item.status)))
  if (activeFilter.value === 'Escalated') rows = rows.filter((item) => item.status === 'Escalated' || item.is_escalated)
  if (activeFilter.value === 'New') rows = rows.filter((item) => ['New', 'Received'].includes(item.status))
  if (activeFilter.value === 'Assigned') rows = rows.filter((item) => Boolean(item.assigned_user_id || item.assigned_officer_name))
  if (activeFilter.value === 'In progress') rows = rows.filter((item) => ['Under Review', 'Action Required', 'Awaiting Response', 'Escalated'].includes(item.status))
  if (activeFilter.value === 'Resolved') rows = rows.filter((item) => ['Disposed', 'Closed', 'Resolved'].includes(item.status))
  if (activeFilter.value === 'My Assigned Cases' || activeFilter.value === 'My Cases') {
    rows = rows.filter((item) => item.assigned_user_id === auth.user?.id || (item.assigned_officer_name && auth.user?.name && item.assigned_officer_name.toLowerCase().includes(auth.user.name.toLowerCase())))
  }
  if (activeFilter.value === 'Bureau-Wide Cases' || activeFilter.value === 'Bureau Cases') {
    const bCode = auth.user?.bureau_code
    const bId = auth.user?.bureau_id
    rows = rows.filter((item) => (bCode && (item.current_bureau_code === bCode || item.receiving_bureau_code === bCode)) || (bId && (item.current_bureau_id === bId || item.receiving_bureau_id === bId)))
  }
  if (activeFilter.value === 'Priority & Escalation Queue' || activeFilter.value === 'Priority / Escalated') {
    rows = rows.filter((item) => item.status === 'Escalated' || item.priority === 'Critical' || item.is_escalated || item.is_overdue || (item.due_at && new Date(item.due_at).getTime() < Date.now()))
  }
  if (activeFilter.value === 'Approaching Deadlines' || activeFilter.value === 'Due Soon') {
    rows = rows.filter((item) => item.is_overdue || (item.due_at && (new Date(item.due_at).getTime() - Date.now() < 3 * 86400000) && !['Disposed', 'Closed'].includes(item.status)))
  }
  return rows
})

const pagedComplaints = computed(() => visibleComplaints.value.slice((pageNumber.value - 1) * pageSize, pageNumber.value * pageSize))
const complaintPageCount = computed(() => Math.max(1, Math.ceil(visibleComplaints.value.length / pageSize)))
const visibleInstitutions = computed(() => {
  let rows = [...institutions.value]
  if (globalQuery.value) rows = rows.filter((item) => [item.name, item.institution_code, item.state, item.district, ...(item.aliases || [])].join(' ').toLowerCase().includes(globalQuery.value))
  if (institutionTypeFilter.value !== 'All types') rows = rows.filter((item) => item.institution_type === institutionTypeFilter.value)
  return rows
})
const visibleOverlaps = computed(() => {
  let rows = [...overlaps.value]
  if (overlapFilter.value !== 'all') rows = rows.filter((item) => item.review_status === overlapFilter.value || (overlapFilter.value === 'pending' && !item.review_status))
  if (globalQuery.value) rows = rows.filter((item) => JSON.stringify(item).toLowerCase().includes(globalQuery.value))
  return rows
})
const visibleNotifications = computed(() => {
  let rows = [...notifications.value]
  if (notificationFilter.value === 'unread') rows = rows.filter((item) => !item.is_read && !item.read_at)
  if (globalQuery.value) rows = rows.filter((item) => `${item.title} ${item.message}`.toLowerCase().includes(globalQuery.value))
  return rows
})
const bureauWorkload = computed<Row[]>(() => bureaus.value.map((bureau: Row): Row => {
  const rows = complaints.value.filter((item) => (item.current_bureau_code || item.receiving_bureau_code) === bureau.code)
  return { ...bureau, total: rows.length, open: rows.filter((item) => !['Disposed', 'Closed'].includes(item.status)).length, overdue: rows.filter((item) => item.is_overdue).length }
}).sort((a, b) => b.total - a.total))
const categoryWorkload = computed(() => {
  const map: Record<string, { total: number; open: number; overdue: number }> = {}
  complaints.value.forEach((c) => {
    const cat = c.category || 'General administration'
    if (!map[cat]) map[cat] = { total: 0, open: 0, overdue: 0 }
    map[cat].total++
    if (!['Disposed', 'Closed', 'Resolved'].includes(c.status)) map[cat].open++
    if (c.is_overdue) map[cat].overdue++
  })
  return Object.entries(map).map(([category, stats]) => ({ category, ...stats })).sort((a, b) => b.total - a.total)
})
const deadlineList = computed(() => overdueComplaints.value.slice(0, 3))
const institutionTypeOptions = computed(() => ['All types', ...new Set(institutions.value.map((item) => item.institution_type).filter(Boolean))])

function statusClass(status = '') {
  const normalized = String(status).toLowerCase()
  if (['disposed', 'closed', 'resolved', 'confirmed'].includes(normalized)) return 'status-good'
  if (['escalated', 'critical', 'action required', 'overdue'].includes(normalized)) return 'status-critical'
  if (['under review', 'awaiting response', 'pending', 'deferred'].includes(normalized)) return 'status-pending'
  if (['received', 'new'].includes(normalized)) return 'status-new'
  return 'status-neutral'
}
function priorityClass(priority = '') {
  const p = String(priority).toLowerCase()
  if (p === 'critical') return 'priority-critical'
  if (p === 'high') return 'priority-high'
  if (p === 'medium') return 'priority-medium'
  return 'priority-low'
}
function shortDate(value?: string | null) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(date)
}
function dateTime(value?: string | null) {
  if (!value) return 'No action recorded'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }).format(date)
}
function formatActionType(type?: string | null): string {
  if (!type) return 'Case action'
  const map: Record<string, string> = {
    case_intake: 'Complaint received',
    status_change: 'Status updated',
    next_action_update: 'Next action set',
    officer_reassigned: 'Officer assigned',
    officer_assigned: 'Officer assigned',
    transfer_requested: 'Transfer initiated',
    bureau_transferred: 'Bureau transferred',
    coordination_note_added: 'Note added',
    query_to_complainant: 'Inquiry sent',
    complainant_response: 'Complainant responded',
    case_escalated: 'Case escalated',
    case_linked: 'Case linked',
  }
  return map[type] || type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}
function daysLate(item: Row) {
  if (!item.due_at) return 0
  return Math.max(0, Math.floor((Date.now() - new Date(item.due_at).getTime()) / 86400000))
}
function getCaseForLink(link: Row, side: 'a' | 'b') {
  const embedded = side === 'a' ? link.case_a : link.case_b
  if (embedded) return embedded
  const id = side === 'a' ? link.complaint_id_a : link.complaint_id_b
  return complaints.value.find((item) => Number(item.id) === Number(id)) || { case_number: `Case ${id}`, subject: 'Case information unavailable' }
}
function navigateToComplaint(id: number | string) { router.push(`/complaints/${id}`) }
function navigateToInstitution(id: number | string) { router.push(`/institutions/${id}`) }
function persistDemoData() {
  if (!ui.isDemoMode) return
  saveStored('casework_demo_complaints', complaints.value)
  saveStored('casework_demo_institutions', institutions.value)
  saveStored('casework_demo_overlaps', overlaps.value)
  saveStored('casework_demo_notifications', notifications.value)
}

async function safeGet(url: string, params?: Row) {
  try { return (await apiClient.get(url, { params })).data } catch { return null }
}
async function loadWorkspace() {
  loading.value = true
  if (route.query.demo === '1') {
    forceDemoMode.value = true
    sessionStorage.setItem('casework_demo_mode', '1')
  }
  if (forceDemoMode.value) {
    ui.isDemoMode = true
    kpis.value = {}
    complaints.value = readStored('casework_demo_complaints', sampleComplaints)
    institutions.value = readStored('casework_demo_institutions', sampleInstitutions)
    overlaps.value = readStored('casework_demo_overlaps', sampleOverlaps)
    notifications.value = readStored('casework_demo_notifications', sampleNotifications)
    if (page.value === 'admin') {
      adminUsers.value = [
        { id: 1, name: 'System Administrator', email: 'admin@aicte.gov.in', role: 'admin', is_active: true },
        { id: 2, name: 'Ananya Rao', email: 'officer.pgrc@aicte.gov.in', role: 'officer', bureau_name: 'PGRC', is_active: true },
        { id: 3, name: 'Vikram Nair', email: 'officer.ab@aicte.gov.in', role: 'officer', bureau_name: 'Approval Bureau', is_active: true },
        { id: 4, name: 'Monitoring Director', email: 'director.monitoring@aicte.gov.in', role: 'senior_authority', is_active: true },
      ]
      auditLogs.value = []
      systemStatus.value = { status: 'Demo mode', database: 'Not connected', portal_version: 'SIH 2026 prototype' }
    }
    if (page.value === 'imports') importHistory.value = []
    ui.unreadNotifications = unreadCount.value
    loading.value = false
    return
  }
  const responses = await Promise.all([
    safeGet('/reports/kpis'),
    safeGet('/complaints', { page: 1, per_page: 100 }),
    safeGet('/institutions', { page: 1, per_page: 100 }),
    safeGet('/overlaps', { review_status: 'all' }),
    safeGet('/notifications'),
    safeGet('/bureaus'),
  ])
  const [kpiData, complaintData, institutionData, overlapData, notificationData, bureauData] = responses
  const successCount = responses.filter((item) => item !== null).length
  ui.isDemoMode = successCount < responses.length
  if (kpiData) kpis.value = kpiData
  if (complaintData) complaints.value = complaintData.items || complaintData.complaints || []
  if (institutionData) institutions.value = institutionData.items || institutionData.institutions || []
  if (overlapData) overlaps.value = overlapData.overlaps || []
  if (notificationData) notifications.value = notificationData.notifications || notificationData.items || []
  if (bureauData?.bureaus?.length) bureaus.value = bureauData.bureaus
  if (!complaintData) complaints.value = readStored('casework_demo_complaints', sampleComplaints)
  if (!institutionData) institutions.value = readStored('casework_demo_institutions', sampleInstitutions)
  if (!overlapData) overlaps.value = readStored('casework_demo_overlaps', sampleOverlaps)
  if (!notificationData) notifications.value = readStored('casework_demo_notifications', sampleNotifications)
  if (page.value === 'admin') {
    const [users, logs, status, industries, settings] = await Promise.all([
      safeGet('/admin/users'),
      safeGet('/admin/audit-logs'),
      safeGet('/admin/system-status'),
      safeGet('/admin/industries'),
      safeGet('/admin/settings'),
    ])
    adminUsers.value = users?.users || [
      { id: 1, name: 'Dr. Rajiv Sharma', email: 'admin@aicte.gov.in', role: 'SYSTEM_ADMIN', designation: 'Chief System Administrator & Director (IT)', is_active: true },
      { id: 2, name: 'Smt. Ananya Sen', email: 'officer.pgrc@aicte.gov.in', role: 'INDUSTRY', bureau_name: 'PGRC', designation: 'Senior Grievance Officer', is_active: true },
      { id: 3, name: 'Grievance Redressal Industry Desk', email: 'industry@aicte.gov.in', role: 'INDUSTRY', bureau_name: 'PGRC', designation: 'Lead Coordinator', is_active: true },
      { id: 4, name: 'Pooja Sharma (Student Complainant)', email: 'user@aicte.gov.in', role: 'USER', designation: 'Citizen Complainant', is_active: true },
    ]
    auditLogs.value = logs?.audit_logs || []
    systemStatus.value = status || { status: successCount ? 'API available' : 'Demo mode', database: successCount ? 'Status not verified' : 'Not connected', portal_version: 'AICTE-CMP v2.0-SIH2026' }
    if (industries?.industries) adminIndustries.value = industries.industries
    if (settings?.settings) adminSettings.value = settings.settings
  }
  if (page.value === 'imports') {
    const history = await safeGet('/imports/history')
    importHistory.value = history?.batches || []
  }
  ui.unreadNotifications = unreadCount.value
  loading.value = false
}
async function refreshWorkspace() {
  refreshing.value = true
  await loadWorkspace()
  refreshing.value = false
  toastLocal(ui.isDemoMode ? 'Refreshed the local demonstration data.' : 'Workspace data refreshed.', 'info')
}

async function toggleUserStatus(u: Row) {
  try {
    if (ui.isDemoMode) {
      u.is_active = !u.is_active
      toastLocal(`[Demo] Account ${u.name} is now ${u.is_active ? 'Active' : 'Deactivated'}.`)
      return
    }
    await apiClient.patch(`/admin/users/${u.id}`, { is_active: !u.is_active })
    u.is_active = !u.is_active
    toastLocal(`Account ${u.name} is now ${u.is_active ? 'Active' : 'Deactivated'}.`)
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to update account status.', 'error')
  }
}

function openCreateIndustryModal() {
  newIndustryUser.name = ''
  newIndustryUser.email = ''
  newIndustryUser.password = ''
  newIndustryUser.bureau_id = String(bureaus.value[0]?.id || 1)
  newIndustryUser.designation = 'Departmental Caseworker'
  newIndustryUser.role = 'INDUSTRY'
  isCreateIndustryOpen.value = true
}

async function submitCreateIndustry() {
  if (!newIndustryUser.name.trim() || !newIndustryUser.email.trim() || !newIndustryUser.password.trim()) {
    toastLocal('Please fill all required fields.', 'error')
    return
  }
  try {
    if (ui.isDemoMode) {
      adminUsers.value.push({
        id: Date.now(),
        name: newIndustryUser.name.trim(),
        email: newIndustryUser.email.trim().toLowerCase(),
        role: 'INDUSTRY',
        bureau_name: bureaus.value.find((b: Row) => String(b.id) === newIndustryUser.bureau_id)?.name || 'Department',
        designation: newIndustryUser.designation,
        is_active: true,
      })
      isCreateIndustryOpen.value = false
      toastLocal(`[Demo] Industry account created for ${newIndustryUser.name}.`)
      return
    }
    await apiClient.post('/admin/users', {
      name: newIndustryUser.name.trim(),
      email: newIndustryUser.email.trim().toLowerCase(),
      password: newIndustryUser.password.trim(),
      bureau_id: Number(newIndustryUser.bureau_id),
      designation: newIndustryUser.designation.trim(),
      role: 'INDUSTRY'
    })
    isCreateIndustryOpen.value = false
    toastLocal(`Industry account ${newIndustryUser.name} created successfully.`)
    await loadWorkspace()
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to create industry account.', 'error')
  }
}

function openResetPassword(u: Row) {
  selectedResetUser.value = u
  newPasswordInput.value = ''
  isResetPasswordOpen.value = true
}

async function submitResetPassword() {
  if (!selectedResetUser.value || !newPasswordInput.value.trim()) return
  try {
    if (ui.isDemoMode) {
      isResetPasswordOpen.value = false
      toastLocal(`[Demo] Password reset for ${selectedResetUser.value.name}.`)
      return
    }
    await apiClient.post(`/admin/users/${selectedResetUser.value.id}/reset-password`, {
      password: newPasswordInput.value.trim()
    })
    isResetPasswordOpen.value = false
    toastLocal(`Password updated for ${selectedResetUser.value.name}.`)
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to reset credentials.', 'error')
  }
}

async function addCategory() {
  const cat = newCategoryInput.value.trim()
  if (!cat) return
  if (adminSettings.value.categories?.includes(cat)) {
    toastLocal('Category already exists.', 'error')
    return
  }
  const next = [...(adminSettings.value.categories || []), cat]
  try {
    if (!ui.isDemoMode) {
      await apiClient.patch('/admin/settings', { categories: next })
    }
    adminSettings.value.categories = next
    newCategoryInput.value = ''
    toastLocal(`Added category '${cat}'.`)
  } catch (err: any) {
    toastLocal('Failed to update categories.', 'error')
  }
}

async function removeCategory(cat: string) {
  const next = (adminSettings.value.categories || []).filter((c: string) => c !== cat)
  try {
    if (!ui.isDemoMode) {
      await apiClient.patch('/admin/settings', { categories: next })
    }
    adminSettings.value.categories = next
    toastLocal(`Removed category '${cat}'.`)
  } catch (err: any) {
    toastLocal('Failed to remove category.', 'error')
  }
}


function openNewComplaint() {
  newForm.subject = ''
  newForm.description = ''
  newForm.institution_id = String(institutions.value[0]?.id || 1)
  newForm.bureau_id = String(bureaus.value[0]?.id || 1)
  newForm.category = 'General administration'
  newForm.priority = 'Medium'
  newForm.due_at = isoDaysFromNow(14).slice(0, 10)
  newComplaintOpen.value = true
}
async function submitNewComplaint() {
  if (!newForm.subject.trim() || !newForm.description.trim()) {
    toastLocal('Add a subject and complaint description before saving.', 'error')
    return
  }
  const bureau = bureaus.value.find((item) => String(item.id) === newForm.bureau_id) || bureaus.value[0]
  const institution = institutions.value.find((item) => String(item.id) === newForm.institution_id) || institutions.value[0]
  const payload = {
    subject: newForm.subject.trim(), description: newForm.description.trim(), institution_id: Number(newForm.institution_id),
    receiving_bureau_id: Number(newForm.bureau_id), current_bureau_id: Number(newForm.bureau_id), category: newForm.category,
    priority: newForm.priority, due_at: new Date(`${newForm.due_at}T12:00:00`).toISOString(),
  }
  try {
    if (ui.isDemoMode) throw new Error('Demo mode: do not submit to API')
    const response = await apiClient.post('/complaints', payload)
    const item = response.data.complaint || response.data
    complaints.value = [item, ...complaints.value]
    toastLocal('Complaint registered in the case register.')
  } catch {
    ui.isDemoMode = true
    const nextId = Math.max(100, ...complaints.value.map((item) => Number(item.id) || 0)) + 1
    const item: Row = {
      id: nextId, case_number: `DEMO-26-${bureau?.code || 'CASE'}-${String(nextId).padStart(4, '0')}`,
      institution_id: Number(institution?.id || newForm.institution_id), institution_name: institution?.name || 'Institution awaiting verification', institution_code: institution?.institution_code || '',
      institution_state: institution?.state || '', category: newForm.category, subject: newForm.subject.trim(), description: newForm.description.trim(),
      receiving_bureau_id: bureau?.id || 1, receiving_bureau_code: bureau?.code || 'PGRC', receiving_bureau_name: bureau?.name || 'PGRC',
      current_bureau_id: bureau?.id || 1, current_bureau_code: bureau?.code || 'PGRC', current_bureau_name: bureau?.name || 'PGRC',
      priority: newForm.priority, status: 'Received', is_overdue: false, received_at: new Date().toISOString(), due_at: new Date(`${newForm.due_at}T12:00:00`).toISOString(), created_at: new Date().toISOString(),
    }
    complaints.value = [item, ...complaints.value]
    toastLocal('Added to the local demo register. It has not been sent to a live system.', 'info')
  }
  persistDemoData()
  newComplaintOpen.value = false
  router.replace('/complaints')
}

async function changeStatus(status: string) {
  const item = currentComplaint.value
  if (!item) return
  try {
    if (ui.isDemoMode) throw new Error('Demo mode: keep the change local')
    const response = await apiClient.post(`/complaints/${item.id}/actions`, { status, remarks: 'Status updated from the casework portal.' })
    const updated = response.data.complaint || { ...item, status }
    complaints.value = complaints.value.map((row) => Number(row.id) === Number(item.id) ? { ...row, ...updated } : row)
    toastLocal('Case status updated.')
  } catch {
    ui.isDemoMode = true
    complaints.value = complaints.value.map((row) => Number(row.id) === Number(item.id) ? { ...row, status, is_overdue: false, last_action_at: new Date().toISOString() } : row)
    toastLocal('Updated the local demo record. No live system was changed.', 'info')
  }
  persistDemoData()
}
async function reviewOverlap(link: Row, decision: 'Confirmed Overlap' | 'False Alert' | 'Needs Review') {
  if (isReviewing.value) return
  isReviewing.value = true
  const statusMap: Record<string, string> = { 'Confirmed Overlap': 'confirmed', 'False Alert': 'dismissed', 'Needs Review': 'deferred' }
  try {
    if (!ui.isDemoMode) {
      await apiClient.post(`/overlaps/${link.id}/verify`, {
        status: decision,
        remarks: overlapReviewRemarks.value.trim() || `Verified as ${decision} by officer`
      })
    }
    overlaps.value = overlaps.value.map((item) => Number(item.id) === Number(link.id) ? { ...item, review_status: statusMap[decision] || 'confirmed', relationship_type: decision } : item)
    toastLocal(`Decision recorded: ${decision}.`)
    await loadWorkspace()
  } catch {
    ui.isDemoMode = true
    overlaps.value = overlaps.value.map((item) => Number(item.id) === Number(link.id) ? { ...item, review_status: statusMap[decision], relationship_type: decision, review_remarks: 'Reviewed in local demo mode.', reviewed_at: new Date().toISOString() } : item)
    toastLocal(`Decision saved: ${decision}.`, 'info')
  } finally {
    isReviewing.value = false
    selectedOverlap.value = null
    overlapReviewRemarks.value = ''
    persistDemoData()
  }
}

async function submitNextAction() {
  const item = currentComplaint.value
  if (!item || !nextActionText.value.trim()) return
  try {
    const res = await apiClient.post(`/complaints/${item.id}/next-action`, {
      next_action: nextActionText.value.trim(),
      next_action_due: nextActionDueDate.value ? new Date(nextActionDueDate.value).toISOString() : null,
      assignee: nextActionAssignee.value.trim() || null
    })
    item.next_action = nextActionText.value.trim()
    item.next_action_due = nextActionDueDate.value || null
    item.next_action_assignee = nextActionAssignee.value.trim() || null
    isNextActionOpen.value = false
    toastLocal('Next action updated.')
    await loadWorkspace()
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to update next action', 'error')
  }
}

async function submitCoordinationNote() {
  const item = currentComplaint.value
  if (!item || !coordinationNoteText.value.trim()) return
  try {
    const res = await apiClient.post(`/complaints/${item.id}/coordination-note`, {
      note: coordinationNoteText.value.trim()
    })
    item.coordination_notes = res.data.coordination_notes || (item.coordination_notes ? item.coordination_notes + '\n' : '') + coordinationNoteText.value.trim()
    isCoordinationNoteOpen.value = false
    coordinationNoteText.value = ''
    toastLocal('Coordination note recorded.')
    await loadWorkspace()
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to record note', 'error')
  }
}

async function submitRequestInfo() {
  const item = currentComplaint.value
  if (!item || !requestInfoQuery.value.trim()) return
  try {
    await apiClient.post(`/complaints/${item.id}/request-info`, {
      query: requestInfoQuery.value.trim()
    })
    item.status = 'Awaiting Response'
    item.query_to_complainant = requestInfoQuery.value.trim()
    isRequestInfoOpen.value = false
    requestInfoQuery.value = ''
    toastLocal('Information query sent to complainant.')
    await loadWorkspace()
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to request info', 'error')
  }
}

async function submitTransfer() {
  const item = currentComplaint.value
  if (!item || !transferBureauId.value) return
  try {
    await apiClient.post(`/complaints/${item.id}/transfer`, {
      target_bureau_id: Number(transferBureauId.value),
      remarks: transferReason.value.trim() || 'Transferred for administrative jurisdiction'
    })
    isTransferOpen.value = false
    transferReason.value = ''
    toastLocal('Case successfully transferred.')
    await loadWorkspace()
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to transfer case', 'error')
  }
}

async function submitEscalate() {
  const item = currentComplaint.value
  if (!item) return
  try {
    await apiClient.post(`/complaints/${item.id}/escalate`, {
      reason: escalateReason.value.trim() || 'Escalated due to repeated delays'
    })
    item.is_escalated = true
    item.status = 'Escalated'
    isEscalateOpen.value = false
    escalateReason.value = ''
    toastLocal('Case marked as escalated.')
    await loadWorkspace()
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to escalate case', 'error')
  }
}

async function submitLinkCase() {
  const item = currentComplaint.value
  if (!item || !linkCaseNumber.value.trim()) return
  try {
    await apiClient.post(`/complaints/${item.id}/link`, {
      target_ticket: linkCaseNumber.value.trim(),
      notes: linkCaseNotes.value.trim() || 'Linked manually by bureau official'
    })
    isLinkCaseOpen.value = false
    linkCaseNumber.value = ''
    linkCaseNotes.value = ''
    toastLocal('Related case successfully linked.')
    await loadWorkspace()
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to link case', 'error')
  }
}

async function submitReassign() {
  const item = currentComplaint.value
  if (!item || !reassignOfficerId.value) return
  try {
    await apiClient.patch(`/complaints/${item.id}/assign`, {
      assigned_user_id: Number(reassignOfficerId.value)
    })
    isReassignOpen.value = false
    toastLocal('Case reassigned successfully.')
    await loadWorkspace()
  } catch (err: any) {
    toastLocal(err?.response?.data?.error || 'Failed to reassign case', 'error')
  }
}
async function markRead(item: Row) {
  try {
    if (ui.isDemoMode) throw new Error('Demo mode: keep notification state local')
    await apiClient.patch(`/notifications/${item.id}/read`)
  } catch { ui.isDemoMode = true }
  notifications.value = notifications.value.map((row) => Number(row.id) === Number(item.id) ? { ...row, is_read: true, read_at: new Date().toISOString() } : row)
  ui.unreadNotifications = unreadCount.value
  persistDemoData()
}
async function markAllRead() {
  try { if (ui.isDemoMode) throw new Error('Demo mode'); await apiClient.post('/notifications/read-all') } catch { ui.isDemoMode = true }
  notifications.value = notifications.value.map((row) => ({ ...row, is_read: true, read_at: row.read_at || new Date().toISOString() }))
  ui.unreadNotifications = 0
  persistDemoData()
  toastLocal('All notifications marked as read.')
}
function exportDemoCsv() {
  const headers = ['Case ID', 'Institution', 'Subject', 'Bureau', 'Status', 'Priority', 'Received', 'Due date']
  const lines = visibleComplaints.value.map((row) => [row.case_number, row.institution_name, row.subject, row.current_bureau_code || row.receiving_bureau_code, row.status, row.priority, shortDate(row.received_at), shortDate(row.due_at)].map((cell) => `"${String(cell || '').replace(/"/g, '""')}"`).join(','))
  const blob = new Blob([[headers.join(','), ...lines].join('\r\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = 'casework-register-demo.csv'
  anchor.click()
  URL.revokeObjectURL(url)
  toastLocal(ui.isDemoMode ? 'Downloaded the current demo register as CSV.' : 'CSV export downloaded.')
}
async function exportCsv() {
  if (ui.isDemoMode) { exportDemoCsv(); return }
  try {
    const response = await apiClient.get('/reports/export-csv', { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = 'aicte_complaints_export.csv'
    anchor.click()
    URL.revokeObjectURL(url)
    toastLocal('Report downloaded.')
  } catch { exportDemoCsv() }
}
async function onFilePicked(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] || null
  importPreview.value = null
}
async function previewImport() {
  if (!selectedFile.value) { toastLocal('Choose a CSV file first.', 'error'); return }
  try {
    if (ui.isDemoMode) throw new Error('Demo mode: preview locally')
    const form = new FormData()
    form.append('file', selectedFile.value)
    const response = await apiClient.post('/imports/preview', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    importPreview.value = response.data
    toastLocal('Import preview is ready.', 'info')
  } catch {
    const text = await selectedFile.value.text()
    const rows = text.split(/\r?\n/).filter((line) => line.trim()).length
    importPreview.value = { is_valid: rows > 1, total_rows: Math.max(0, rows - 1), success_rows: Math.max(0, rows - 1), failed_rows: 0, valid_rows: [], errors: [], local_demo: true }
    ui.isDemoMode = true
    toastLocal('Previewed the file locally. Use the API for authoritative validation.', 'info')
  }
}
async function commitImport() {
  if (!importPreview.value) return
  if (importPreview.value.local_demo) {
    toastLocal('Local preview complete. Start the Flask API to commit imported records.', 'info')
    return
  }
  try {
    const response = await apiClient.post('/imports/commit', { valid_rows: importPreview.value.valid_rows, filename: selectedFile.value?.name || 'batch_import.csv' })
    toastLocal(response.data.message || 'Import committed.')
    importPreview.value = null
    selectedFile.value = null
    await loadWorkspace()
  } catch (error: any) { toastLocal(error?.response?.data?.error || 'The import could not be committed.', 'error') }
}
function downloadTemplate() {
  const template = 'institution_code,subject,description,category,priority,receiving_bureau_code,external_reference\nAICTE-DEMO-001,Example complaint,Replace with a fictional or authorized complaint description,General administration,Medium,PGRC,DEMO-REF-001\n'
  const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'complaint-import-template.csv'; a.click(); URL.revokeObjectURL(url)
}
function institutionCaseCount(id: number) { return complaints.value.filter((item) => Number(item.institution_id) === Number(id)).length }
function openReview(link: Row) { selectedOverlap.value = link }
function setStatusFilter(value: string) { statusFilter.value = value; pageNumber.value = 1 }
function setBureauFilter(value: string) { bureauFilter.value = value; pageNumber.value = 1 }
function clearFilters() { statusFilter.value = 'All statuses'; bureauFilter.value = 'All Bureaus'; activeFilter.value = 'All cases'; ui.globalSearch = ''; pageNumber.value = 1 }

watch(() => route.query.action, (action) => { if (action === 'new') openNewComplaint() }, { immediate: true })
watch(() => route.path, (path) => {
  if (path === '/admin' || path === '/imports') loadWorkspace()
  if (path.startsWith('/complaints/')) {
    const id = Number(route.params.id)
    if (id && !complaints.value.some((item) => Number(item.id) === id)) {
      safeGet(`/complaints/${id}`).then((data) => { if (data?.complaint) complaints.value = [data.complaint, ...complaints.value] })
    }
  }
})
watch(() => visibleComplaints.value.length, (length) => {
  if (pageNumber.value > Math.max(1, Math.ceil(length / pageSize))) pageNumber.value = Math.max(1, Math.ceil(length / pageSize))
})
watch(unreadCount, (value) => { ui.unreadNotifications = value }, { immediate: true })
onMounted(() => { loadWorkspace() })
onBeforeUnmount(() => {})
</script>

<template>
  <div class="workspace-view">
    <div v-if="page !== 'detail'" class="page-heading-row">
      <div class="page-heading-copy">
        <h1>{{ pageHeading }}</h1>
        <p v-if="pageSubheading">{{ pageSubheading }}</p>
      </div>
      <div class="page-heading-actions">
        <button class="button button-quiet" :disabled="refreshing" @click="refreshWorkspace"><RefreshCw :size="16" :class="{ 'spin-once': refreshing }" /> Refresh</button>
        <button v-if="['dashboard', 'complaints'].includes(page) && auth.user?.role !== 'senior_authority'" class="button button-primary" @click="openNewComplaint"><Plus :size="17" /> Register complaint</button>
        <button v-else-if="page === 'reports'" class="button button-primary" @click="exportCsv"><Download :size="16" /> Export CSV</button>
        <button v-else-if="page === 'institutions' && auth.user?.role !== 'senior_authority'" class="button button-primary" @click="router.push('/imports')"><Upload :size="16" /> Import records</button>
      </div>
    </div>

    <div v-if="loading" class="loading-line"><LoaderCircle :size="18" class="spin" /> Updating the case register…</div>

    <!-- OVERVIEW -->
    <template v-if="page === 'dashboard'">
      <!-- Six Clearly Defined Industry / Department KPI Buckets -->
      <section class="metric-strip" aria-label="Industry Case Metrics">
        <button type="button" class="metric-cell" @click="activeFilter = 'New'; router.push('/complaints')">
          <span class="metric-label">New</span>
          <strong class="metric-value">{{ newComplaintsCount }}</strong>
        </button>
        <button type="button" class="metric-cell" @click="activeFilter = 'Assigned'; router.push('/complaints')">
          <span class="metric-label">Assigned</span>
          <strong class="metric-value">{{ assignedComplaintsCount }}</strong>
        </button>
        <button type="button" class="metric-cell" @click="activeFilter = 'In progress'; router.push('/complaints')">
          <span class="metric-label">In progress</span>
          <strong class="metric-value metric-warn">{{ inProgressComplaintsCount }}</strong>
        </button>
        <button type="button" class="metric-cell" @click="activeFilter = 'Overdue'; router.push('/complaints')">
          <span class="metric-label">Overdue</span>
          <strong class="metric-value" :class="{ 'metric-danger': overdueCount > 0 }">{{ overdueCount }}</strong>
        </button>
        <button type="button" class="metric-cell" @click="activeFilter = 'Resolved'; router.push('/complaints')">
          <span class="metric-label">Resolved</span>
          <strong class="metric-value">{{ resolvedCount }}</strong>
        </button>
        <button type="button" class="metric-cell" @click="router.push('/overlaps')">
          <span class="metric-label">Potential overlaps</span>
          <strong class="metric-value">{{ overlappingCount }}</strong>
        </button>
      </section>


      <!-- Action Required: Pending Overlap Banner -->
      <div v-if="pendingOverlaps.length" class="overview-notice">
        <div class="notice-symbol"><GitCompare :size="18" /></div>
        <div class="notice-copy">
          <strong>{{ pendingOverlaps.length }} case overlap{{ pendingOverlaps.length === 1 ? '' : 's' }} awaiting review</strong>
          <span>Cross-bureau correlation detected between {{ getCaseForLink(pendingOverlaps[0], 'a').case_number }} and {{ getCaseForLink(pendingOverlaps[0], 'b').case_number }}.</span>
        </div>
        <div class="notice-actions">
          <button class="button button-small button-quiet" @click="openReview(pendingOverlaps[0])">Compare records</button>
          <button class="button button-small button-primary" @click="router.push('/overlaps')">Review queue <ArrowRight :size="13" /></button>
        </div>
      </div>

      <!-- Main Section: Recent Cases (Full Width) -->
      <section class="content-section cases-section">
        <div class="section-heading">
          <div>
            <h2>Recent cases</h2>
            <p>Latest entries in the register</p>
          </div>
          <button class="text-action" @click="router.push('/complaints')">All complaints <ArrowRight :size="15" /></button>
        </div>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Subject & institution</th>
                <th>Bureau</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Due date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recentComplaints" :key="item.id" class="clickable-row" @click="navigateToComplaint(item.id)">
                <td><span class="case-id">{{ item.case_number }}</span></td>
                <td>
                  <div class="case-cell">
                    <strong>{{ item.subject }}</strong>
                    <small>{{ item.institution_name || 'Institution not available' }}</small>
                  </div>
                </td>
                <td><span class="bureau-tag">{{ item.current_bureau_code || item.receiving_bureau_code || '—' }}</span></td>
                <td><span class="status-label" :class="statusClass(item.status)"><i></i>{{ item.status }}</span></td>
                <td><span class="priority-label" :class="priorityClass(item.priority)">{{ item.priority }}</span></td>
                <td><span :class="{ 'date-overdue': item.is_overdue }">{{ shortDate(item.due_at) }}</span></td>
                <td><ChevronRight :size="16" class="row-arrow" /></td>
              </tr>
              <tr v-if="!recentComplaints.length">
                <td colspan="7" class="empty-cell">No complaint records available.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-foot">
          <span>{{ recentComplaints.length }} records</span>
          <span>Updated {{ shortDate(new Date().toISOString()) }}</span>
        </div>
      </section>

      <!-- Bottom Analytics: Clean 2-column distribution and intake -->
      <div class="lower-grid">
        <section class="content-section bureau-section">
          <div class="section-heading">
            <div>
              <h2>Work by bureau</h2>
              <p>Current distribution across AICTE cells</p>
            </div>
            <button class="text-action" @click="router.push('/reports')">View reports <ArrowRight :size="15" /></button>
          </div>
          <div class="bureau-table">
            <div v-for="bureau in bureauWorkload" :key="bureau.code" class="bureau-row">
              <div class="bureau-name">
                <span class="bureau-avatar">{{ bureau.code.slice(0, 2) }}</span>
                <span><strong>{{ bureau.code }}</strong><small>{{ bureau.name }}</small></span>
              </div>
              <div class="bureau-track"><span :style="{ width: `${Math.max(3, (bureau.total / Math.max(1, ...bureauWorkload.map((b: Row) => b.total))) * 100)}%` }"></span></div>
              <div class="bureau-count"><strong>{{ bureau.total }}</strong><small>{{ bureau.open }} open</small></div>
            </div>
          </div>
        </section>

        <section class="content-section category-section">
          <div class="section-heading">
            <div>
              <h2>Workload by Category</h2>
              <p>Active institutional complaints by category</p>
            </div>
            <button class="text-action" @click="router.push('/reports')">View details <ArrowRight :size="15" /></button>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Total</th>
                  <th>Open</th>
                  <th>Overdue</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="cat in categoryWorkload.slice(0, 5)" :key="cat.category">
                  <td><strong>{{ cat.category }}</strong></td>
                  <td class="font-mono">{{ cat.total }}</td>
                  <td class="font-mono text-primary font-bold">{{ cat.open }}</td>
                  <td class="font-mono text-red-700 font-bold">{{ cat.overdue }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </template>

    <!-- COMPLAINT REGISTER -->
    <template v-else-if="page === 'complaints'">
      <section class="filter-bar">
        <div class="segmented-filter" role="group" aria-label="Case state filter">
          <button
            v-for="choice in ['All cases', 'My Cases', 'Bureau Cases', 'Priority / Escalated', 'Due Soon']"
            :key="choice"
            :class="{ selected: activeFilter === choice }"
            @click="activeFilter = choice; pageNumber = 1"
          >
            {{ choice }}
            <span v-if="choice === 'Priority / Escalated'">{{ overdueComplaints.length }}</span>
          </button>
        </div>
        <div class="filter-controls">
          <label class="select-control"><Filter :size="15" /><select v-model="statusFilter" aria-label="Filter by status"><option>All statuses</option><option>Received</option><option>Under Review</option><option>Action Required</option><option>Awaiting Response</option><option>Escalated</option><option>Disposed</option><option>Closed</option></select><ChevronDown :size="14" /></label>
          <label class="select-control"><Layers3 :size="15" /><select v-model="bureauFilter" aria-label="Filter by Bureau"><option>All Bureaus</option><option v-for="bureau in bureaus" :key="bureau.code" :value="bureau.code">{{ bureau.code }}</option></select><ChevronDown :size="14" /></label>
          <button class="button button-quiet button-small" @click="clearFilters"><X :size="14" /> Clear</button>
        </div>
      </section>
      <section class="content-section register-table-section">
        <div class="section-heading table-title-row"><div><h2>Case register</h2><p>{{ visibleComplaints.length }} records match the current filters</p></div><button class="button button-quiet button-small" @click="exportCsv"><Download :size="15" /> Export</button></div>
        <div class="table-wrap">
          <table class="data-table register-table">
            <thead><tr><th>Case ID</th><th>Institution & Permanent ID</th><th>Complaint Subject</th><th>Bureau</th><th>Status</th><th>Priority</th><th>Next Action Required</th><th>Ageing</th><th>Due Date</th><th></th></tr></thead>
            <tbody>
              <tr v-for="item in pagedComplaints" :key="item.id" class="clickable-row" @click="navigateToComplaint(item.id)">
                <td><span class="case-id">{{ item.case_number }}</span></td>
                <td>
                  <button class="table-link" @click.stop="navigateToInstitution(item.institution_id)">{{ item.institution_name }}</button>
                  <small class="table-subline font-mono font-bold text-primary">{{ item.institution_code || '1-XXXXXXXX' }}</small>
                </td>
                <td><div class="case-cell"><strong>{{ item.subject }}</strong><small>{{ item.category }}</small></div></td>
                <td><span class="bureau-tag">{{ item.current_bureau_code || item.receiving_bureau_code }}</span></td>
                <td><span class="status-label" :class="statusClass(item.status)"><i></i>{{ item.status }}</span></td>
                <td><span class="priority-label" :class="priorityClass(item.priority)">{{ item.priority }}</span></td>
                <td>
                  <span class="text-xs font-medium text-slate-800">{{ item.next_action || 'Review required' }}</span>
                </td>
                <td>
                  <span class="bureau-tag">{{ item.ageing_days ?? daysLate(item) }}d</span>
                </td>
                <td><span :class="{ 'date-overdue': item.is_overdue }">{{ shortDate(item.due_at) }}</span></td>
                <td><ChevronRight :size="15" class="row-arrow" /></td>
              </tr>
              <tr v-if="!pagedComplaints.length"><td colspan="10" class="empty-cell">No cases match these filters. <button class="inline-link" @click.stop="clearFilters">Clear filters</button></td></tr>
            </tbody>
          </table>
        </div>
        <div class="pagination-row"><span>Page {{ pageNumber }} of {{ complaintPageCount }}</span><div class="pagination-controls"><button class="icon-button" :disabled="pageNumber <= 1" aria-label="Previous page" @click="pageNumber--"><ChevronLeft :size="17" /></button><button class="page-number">{{ pageNumber }}</button><button class="icon-button" :disabled="pageNumber >= complaintPageCount" aria-label="Next page" @click="pageNumber++"><ChevronRight :size="17" /></button></div></div>
      </section>
    </template>

    <!-- COMPLAINT DETAIL -->
    <template v-else-if="page === 'detail'">
      <div v-if="currentComplaint" class="detail-layout">
        <div class="detail-main-column">
          <section class="content-section detail-summary">
            <div class="detail-topline">
              <button class="back-link" @click="router.push('/complaints')"><ChevronLeft :size="15" /> All complaints</button>
              <div class="flex items-center gap-2">
                <button class="button button-quiet button-small" :disabled="refreshing" @click="refreshWorkspace">
                  <RefreshCw :size="13" :class="{ 'spin-once': refreshing }" /> Refresh
                </button>
                <span class="bureau-tag">Pending {{ currentComplaint.ageing_days ?? daysLate(currentComplaint) }} days</span>
                <span class="case-id">{{ currentComplaint.case_number }}</span>
              </div>
            </div>

            <!-- Escalation Notice if active -->
            <div v-if="currentComplaint.is_escalated" class="p-3 my-2 rounded bg-red-100 border border-red-300 text-red-900 text-xs font-semibold flex items-center gap-2">
              <AlertTriangle :size="16" class="text-red-700 flex-none" />
              <span>Escalated Case: {{ currentComplaint.escalation_reason || 'Flagged for Senior Bureau Authority review.' }}</span>
            </div>

            <div class="detail-title-row">
              <div>
                <h2>{{ currentComplaint.subject }}</h2>
                <p>
                  {{ currentComplaint.institution_name }}
                  <span v-if="currentComplaint.institution_code" class="font-mono text-xs font-bold text-primary ml-1">
                    (Permanent ID: {{ currentComplaint.institution_code }})
                  </span>
                  <span class="meta-dot"></span> {{ currentComplaint.category }}
                </p>
              </div>
              <span class="status-label" :class="statusClass(currentComplaint.status)"><i></i>{{ currentComplaint.status }}</span>
            </div>

            <div class="detail-meta-grid">
              <div><span>Received</span><strong>{{ shortDate(currentComplaint.received_at) }}</strong></div>
              <div><span>Due date</span><strong :class="{ 'date-overdue': currentComplaint.is_overdue }">{{ shortDate(currentComplaint.due_at) }}</strong></div>
              <div><span>Current Bureau</span><strong>{{ currentComplaint.current_bureau_name || currentComplaint.current_bureau_code }}</strong></div>
              <div><span>Assigned officer</span><strong>{{ currentComplaint.assigned_officer_name || 'Unassigned' }}</strong></div>
            </div>

            <div class="detail-description">
              <h3>Complaint summary</h3>
              <p class="[text-wrap:pretty]">{{ currentComplaint.description }}</p>
            </div>
          </section>

          <!-- Next Action Card -->
          <section class="content-section" style="padding: 14px 18px;">
            <div class="flex items-center justify-between mb-2">
              <div>
                <h3 style="font-size: 13px; font-weight: 700; margin: 0;">Next Action</h3>
              </div>
              <button class="button button-quiet button-small" @click="isNextActionOpen = true">
                <Sliders :size="13" /> Update
              </button>
            </div>
            <div style="font-size: 12px; font-weight: 600; color: var(--primary);">
              {{ currentComplaint.next_action || 'Pending review' }}
            </div>
            <div class="flex gap-4 mt-2 text-xs text-quiet">
              <span>Target Due: <strong>{{ shortDate(currentComplaint.next_action_due) }}</strong></span>
              <span>Assignee: <strong>{{ currentComplaint.next_action_assignee || currentComplaint.assigned_officer_name || 'Assigned Officer' }}</strong></span>
            </div>
          </section>

          <!-- Active Complainant Query & Response -->
          <section v-if="currentComplaint.query_to_complainant || currentComplaint.status === 'Awaiting Response'" class="content-section" style="padding: 14px 18px; border-left: 3px solid #f59e0b;">
            <h3 style="font-size: 13px; font-weight: 700; color: #b45309; margin: 0 0 6px;">Complainant Clarification Status</h3>
            <div style="font-size: 12px; margin-bottom: 8px;">
              <strong>Query Sent:</strong> {{ currentComplaint.query_to_complainant }}
            </div>
            <div v-if="currentComplaint.complainant_response" style="font-size: 12px; color: #15803d; background: rgba(34,197,94,0.1); padding: 8px; border-radius: 4px;">
              <strong>Complainant Response:</strong> {{ currentComplaint.complainant_response }}
              <div v-if="currentComplaint.additional_documents" class="mt-1 font-mono text-xs text-slate-700">
                Attached: {{ currentComplaint.additional_documents }}
              </div>
            </div>
            <div v-else style="font-size: 12px; color: var(--muted); font-style: italic;">
              Awaiting response from complainant via public portal.
            </div>
          </section>

          <!-- Cross-Bureau Coordination Notes -->
          <section class="content-section" style="padding: 14px 18px;">
            <div class="flex items-center justify-between mb-2">
              <div>
                <h3 style="font-size: 13px; font-weight: 700; margin: 0;">Coordination Notes</h3>
              </div>
              <button class="button button-quiet button-small" @click="isCoordinationNoteOpen = true">
                <Plus :size="13" /> Add Note
              </button>
            </div>
            <div v-if="currentComplaint.coordination_notes" style="white-space: pre-line; font-size: 12px; line-height: 1.5; padding: 10px; background: var(--canvas); border-radius: 4px; border: 1px solid var(--line);">
              {{ currentComplaint.coordination_notes }}
            </div>
            <div v-else style="font-size: 12px; color: var(--muted);">
              No coordination notes recorded yet.
            </div>
          </section>

          <section class="content-section timeline-section">
            <div class="section-heading"><div><h2>Case history</h2></div></div>
            <div v-if="currentComplaint.actions?.length" class="timeline-list">
              <div v-for="action in currentComplaint.actions" :key="action.id" class="timeline-item"><span class="timeline-point"></span><div><div class="timeline-item-head"><strong>{{ formatActionType(action.action_type) }}</strong><span>{{ dateTime(action.created_at) }}</span></div><p>{{ action.description }}</p><small>{{ action.performed_by_name || 'Authorized officer' }}</small></div></div>
            </div>
            <div v-else class="timeline-empty"><span class="timeline-point"></span><div><strong>Complaint registered</strong><p>The case record was created on {{ shortDate(currentComplaint.created_at || currentComplaint.received_at) }}.</p></div></div>
          </section>
        </div>
        <aside class="detail-side-column">
          <section class="content-section action-panel">
            <div class="section-heading"><div><h2>Case Actions</h2></div></div>
            <label class="field-label" for="case-status">Status</label>
            <select id="case-status" class="form-control" :value="currentComplaint.status" @change="changeStatus(($event.target as HTMLSelectElement).value)">
              <option>Received</option>
              <option>Under Review</option>
              <option>Action Required</option>
              <option>Awaiting Response</option>
              <option>Escalated</option>
              <option>Disposed</option>
              <option>Closed</option>
            </select>

            <div class="space-y-2 mt-4 pt-3 border-t border-line">
              <button class="button button-quiet w-full" @click="isReassignOpen = true">
                <Users :size="14" /> Assign Officer
              </button>
              <button class="button button-quiet w-full" @click="isTransferOpen = true">
                <Layers3 :size="14" /> Transfer Bureau
              </button>
              <button class="button button-quiet w-full" @click="isRequestInfoOpen = true">
                <Search :size="14" /> Request Complainant Info
              </button>
              <button class="button button-quiet w-full" @click="isLinkCaseOpen = true">
                <GitCompare :size="14" /> Link Related Case
              </button>
              <button class="button button-quiet w-full" @click="isEscalateOpen = true">
                <CircleAlert :size="14" /> Escalate Case
              </button>
            </div>
          </section>
          <section class="content-section related-panel">
            <div class="section-heading"><div><h2>Related cases</h2></div></div>
            <div v-for="link in overlaps.filter((item) => Number(item.complaint_id_a) === currentComplaint.id || Number(item.complaint_id_b) === currentComplaint.id)" :key="link.id" class="related-row">
              <span class="related-icon"><GitCompare :size="16" /></span>
              <div>
                <strong>{{ getCaseForLink(link, Number(link.complaint_id_a) === currentComplaint.id ? 'b' : 'a').case_number }}</strong>
                <small>{{ link.review_status === 'pending' ? 'Awaiting review' : link.review_status }}</small>
              </div>
              <button class="icon-button" aria-label="Review relationship" @click="openReview(link)"><ArrowUpRight :size="16" /></button>
            </div>
            <div v-if="!overlaps.some((item) => Number(item.complaint_id_a) === currentComplaint.id || Number(item.complaint_id_b) === currentComplaint.id)" class="quiet-empty">
              <span>No related records flagged.</span>
            </div>
          </section>
        </aside>
      </div>
      <section v-else class="content-section not-found"><CircleAlert :size="25" /><h2>Case not found</h2><p>This case is not in the currently loaded register.</p><button class="button button-primary" @click="router.push('/complaints')">Return to complaints</button></section>
    </template>

    <!-- INSTITUTION DIRECTORY -->
    <template v-else-if="page === 'institutions'">
      <section class="filter-bar institution-filter-bar"><div class="filter-intro"><Building2 :size="19" /><span>{{ visibleInstitutions.length }} institutions in the directory</span></div><div class="filter-controls"><label class="select-control"><Filter :size="15" /><select v-model="institutionTypeFilter" aria-label="Filter by institution type"><option v-for="type in institutionTypeOptions" :key="type">{{ type }}</option></select><ChevronDown :size="14" /></label></div></section>
      <section class="content-section directory-section"><div class="section-heading"><div><h2>Institution records</h2><p>Open a profile to see all associated complaints</p></div></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Institution</th><th>Permanent ID</th><th>Location</th><th>Cases</th><th>Open</th><th>Bureaus involved</th><th></th></tr></thead><tbody><tr v-for="institution in visibleInstitutions" :key="institution.id" class="clickable-row" @click="navigateToInstitution(institution.id)"><td><div class="institution-name-cell"><span class="institution-avatar"><Building2 :size="17" /></span><span><strong>{{ institution.name }}</strong><small>{{ institution.institution_type }}</small></span></div></td><td><span class="case-id">{{ institution.institution_code }}</span></td><td>{{ institution.district ? `${institution.district}, ` : '' }}{{ institution.state }}</td><td><strong>{{ institution.total_complaints ?? institutionCaseCount(institution.id) }}</strong></td><td><span class="open-count">{{ institution.open_complaints ?? complaints.filter((item) => Number(item.institution_id) === Number(institution.id) && !['Disposed', 'Closed'].includes(item.status)).length }}</span></td><td><div class="bureau-stack"><span v-for="code in (institution.bureaus_involved || []).slice(0, 3)" :key="code">{{ code }}</span></div></td><td><ChevronRight :size="16" class="row-arrow" /></td></tr><tr v-if="!visibleInstitutions.length"><td colspan="7" class="empty-cell">No institutions match your search.</td></tr></tbody></table></div></section>
    </template>

    <!-- INSTITUTION PROFILE -->
    <template v-else-if="page === 'institution'">
      <div v-if="currentInstitution" class="institution-profile-page">
        <section class="content-section institution-profile-head"><button class="back-link" @click="router.push('/institutions')"><ChevronLeft :size="15" /> Institution directory</button><div class="institution-profile-name"><div class="institution-large-mark"><Building2 :size="24" /></div><div><div class="case-id">{{ currentInstitution.institution_code }}</div><h2>{{ currentInstitution.name }}</h2><p>{{ currentInstitution.institution_type }} <span class="meta-dot"></span> {{ currentInstitution.district ? `${currentInstitution.district}, ` : '' }}{{ currentInstitution.state }}</p></div></div><div class="profile-stats"><div><span>Total cases</span><strong>{{ currentInstitution.total_complaints ?? institutionCaseCount(currentInstitution.id) }}</strong></div><div><span>Open</span><strong>{{ currentInstitution.open_complaints ?? complaints.filter((item) => Number(item.institution_id) === Number(currentInstitution.id) && !['Disposed', 'Closed'].includes(item.status)).length }}</strong></div><div><span>Disposed</span><strong>{{ currentInstitution.disposed_complaints ?? complaints.filter((item) => Number(item.institution_id) === Number(currentInstitution.id) && ['Disposed', 'Closed'].includes(item.status)).length }}</strong></div><div><span>Bureaus involved</span><strong>{{ (currentInstitution.bureaus_involved || []).length || new Set(complaints.filter((item) => Number(item.institution_id) === Number(currentInstitution.id)).map((item) => item.current_bureau_code)).size }}</strong></div></div></section>
        <section class="content-section"><div class="section-heading"><div><h2>Complaint history</h2><p>Cases linked to this institution, regardless of Bureau</p></div><button class="button button-primary button-small" @click="openNewComplaint"><Plus :size="15" /> Add complaint</button></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Case ID</th><th>Subject</th><th>Bureau</th><th>Status</th><th>Priority</th><th>Received</th><th></th></tr></thead><tbody><tr v-for="item in complaints.filter((row) => Number(row.institution_id) === currentInstitution.id)" :key="item.id" class="clickable-row" @click="navigateToComplaint(item.id)"><td><span class="case-id">{{ item.case_number }}</span></td><td><div class="case-cell"><strong>{{ item.subject }}</strong><small>{{ item.category }}</small></div></td><td><span class="bureau-tag">{{ item.current_bureau_code || item.receiving_bureau_code }}</span></td><td><span class="status-label" :class="statusClass(item.status)"><i></i>{{ item.status }}</span></td><td><span class="priority-label" :class="priorityClass(item.priority)">{{ item.priority }}</span></td><td>{{ shortDate(item.received_at) }}</td><td><ChevronRight :size="15" class="row-arrow" /></td></tr></tbody></table></div></section>
        <section class="content-section"><div class="section-heading"><div><h2>Potential relationships</h2><p>Cases that may need coordination</p></div></div><div v-for="link in overlaps.filter((item) => Number(getCaseForLink(item, 'a').institution_id || item.case_a?.id) && (getCaseForLink(item, 'a').institution_code === currentInstitution.institution_code || getCaseForLink(item, 'b').institution_code === currentInstitution.institution_code || Number(item.case_a?.id) === currentInstitution.id || Number(item.case_b?.id) === currentInstitution.id))" :key="link.id" class="profile-overlap-row"><div><strong>{{ getCaseForLink(link, 'a').case_number }} ↔ {{ getCaseForLink(link, 'b').case_number }}</strong><p>{{ link.match_reason }}</p></div><span class="status-label" :class="statusClass(link.review_status)"><i></i>{{ link.review_status }}</span><button class="text-action" @click="openReview(link)">Review <ArrowRight :size="14" /></button></div><p v-if="!overlaps.length" class="empty-note">No potential relationships are currently recorded.</p></section>
      </div>
      <section v-else class="content-section not-found"><Building2 :size="25" /><h2>Institution not found</h2><p>The institution may not be in the currently loaded directory.</p><button class="button button-primary" @click="router.push('/institutions')">Return to directory</button></section>
    </template>

    <!-- OVERLAP REVIEW -->
    <template v-else-if="page === 'overlaps'">
      <section class="overlap-intro"><div class="overlap-intro-icon"><GitCompare :size="20" /></div><div><strong>Potential relationship is not a duplicate finding.</strong><p>Use the identifiers, subjects and descriptions below to decide whether coordination is appropriate. Original records remain separate.</p></div></section>
      <section class="filter-bar"><div class="segmented-filter" role="group" aria-label="Filter overlap review status"><button v-for="choice in [{ label: 'Awaiting review', value: 'pending' }, { label: 'Confirmed Overlap', value: 'confirmed' }, { label: 'False Alert', value: 'dismissed' }, { label: 'Needs Review', value: 'deferred' }, { label: 'All records', value: 'all' }]" :key="choice.value" :class="{ selected: overlapFilter === choice.value }" @click="overlapFilter = choice.value">{{ choice.label }}</button></div><span class="filter-result-count">{{ visibleOverlaps.length }} relationships</span></section>
      <section class="content-section overlap-table-section"><div class="section-heading"><div><h2>Relationship queue</h2><p>Order reflects the matching signal, not a probability of duplication</p></div></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Cases being compared</th><th>Matching evidence</th><th>Signal</th><th>Review status</th><th>Date flagged</th><th></th></tr></thead><tbody><tr v-for="link in visibleOverlaps" :key="link.id" class="clickable-row" @click="openReview(link)"><td><div class="comparison-cases"><span class="case-id">{{ getCaseForLink(link, 'a').case_number }}</span><span class="compare-divider">↔</span><span class="case-id">{{ getCaseForLink(link, 'b').case_number }}</span><small>{{ getCaseForLink(link, 'a').bureau_code || 'Bureau' }} / {{ getCaseForLink(link, 'b').bureau_code || 'Bureau' }}</small></div></td><td><div class="case-cell"><strong>{{ link.match_method || 'Review suggested' }}</strong><small>{{ link.match_reason }}</small></div></td><td><div class="signal-meter"><strong>{{ Math.round((link.match_score || 0) * 100) }}%</strong><span><i :style="{ width: `${Math.min(100, (link.match_score || 0) * 100)}%` }"></i></span></div></td><td><span class="status-label" :class="statusClass(link.review_status || 'pending')"><i></i>{{ link.review_status || 'pending' }}</span></td><td>{{ shortDate(link.created_at) }}</td><td><button class="button button-quiet button-small" @click.stop="openReview(link)">Compare <ArrowRight :size="14" /></button></td></tr><tr v-if="!visibleOverlaps.length"><td colspan="6" class="empty-cell">No relationship records in this view.</td></tr></tbody></table></div></section>
    </template>

    <!-- REPORTS -->
    <template v-else-if="page === 'reports'">
      <section class="metric-strip report-metrics"><div class="metric-cell"><span class="metric-label">Registered complaints</span><strong class="metric-value">{{ totalCount }}</strong><span class="metric-note">Across the loaded dataset</span></div><div class="metric-cell"><span class="metric-label">Open cases</span><strong class="metric-value">{{ openCount }}</strong><span class="metric-note">Still in progress</span></div><div class="metric-cell"><span class="metric-label">Disposed</span><strong class="metric-value">{{ disposedCount }}</strong><span class="metric-note">Recorded as complete</span></div><div class="metric-cell"><span class="metric-label">Past due</span><strong class="metric-value metric-danger">{{ overdueCount }}</strong><span class="metric-note">Require attention</span></div></section>
      <div class="reports-grid"><section class="content-section report-bureau"><div class="section-heading"><div><h2>Bureau distribution</h2><p>Cases by current handling department</p></div></div><div class="report-bars"><div v-for="bureau in bureauWorkload" :key="bureau.code" class="report-bar-row"><div class="report-bar-head"><span>{{ bureau.name }}</span><strong>{{ bureau.total }}</strong></div><div class="report-bar-track"><span :style="{ width: `${Math.max(2, bureau.total / Math.max(1, ...bureauWorkload.map((b: Row) => b.total)) * 100)}%` }"></span></div><small>{{ bureau.open }} open · {{ bureau.overdue }} past due</small></div></div></section><section class="content-section report-status"><div class="section-heading"><div><h2>Case status</h2><p>Current composition of the register</p></div></div><div class="status-breakdown"><div v-for="status in ['Received', 'Under Review', 'Action Required', 'Awaiting Response', 'Escalated', 'Disposed']" :key="status" class="status-breakdown-row"><span class="status-label" :class="statusClass(status)"><i></i>{{ status }}</span><div class="status-breakdown-track"><span :style="{ width: `${Math.max(0, complaints.filter((item) => item.status === status).length / Math.max(1, complaints.length) * 100)}%` }"></span></div><strong>{{ complaints.filter((item) => item.status === status).length }}</strong></div></div></section></div>
      <section class="content-section report-institution"><div class="section-heading"><div><h2>Institutions with the most open cases</h2><p>Use this list to guide workload review, not as a measure of institutional fault</p></div><button class="text-action" @click="router.push('/institutions')">Institution directory <ArrowRight :size="15" /></button></div><div class="table-wrap"><table class="data-table"><thead><tr><th>Institution</th><th>Permanent ID</th><th>Open cases</th><th>Total cases</th><th></th></tr></thead><tbody><tr v-for="inst in [...institutions].sort((a,b) => (b.open_complaints ?? complaints.filter((c) => Number(c.institution_id) === b.id && !['Disposed','Closed'].includes(c.status)).length) - (a.open_complaints ?? complaints.filter((c) => Number(c.institution_id) === a.id && !['Disposed','Closed'].includes(c.status)).length)).slice(0,5)" :key="inst.id" class="clickable-row" @click="navigateToInstitution(inst.id)"><td><strong>{{ inst.name }}</strong></td><td><span class="case-id">{{ inst.institution_code }}</span></td><td><strong class="report-open-number">{{ inst.open_complaints ?? complaints.filter((c) => Number(c.institution_id) === inst.id && !['Disposed','Closed'].includes(c.status)).length }}</strong></td><td>{{ inst.total_complaints ?? institutionCaseCount(inst.id) }}</td><td><ChevronRight :size="15" class="row-arrow" /></td></tr></tbody></table></div></section>
    </template>

    <!-- NOTIFICATIONS -->
    <template v-else-if="page === 'notifications'">
      <section class="filter-bar"><div class="segmented-filter"><button :class="{ selected: notificationFilter === 'all' }" @click="notificationFilter = 'all'">All activity</button><button :class="{ selected: notificationFilter === 'unread' }" @click="notificationFilter = 'unread'">Unread <span>{{ unreadCount }}</span></button></div><button class="text-action" @click="markAllRead"><CheckCheck :size="15" /> Mark all read</button></section>
      <section class="content-section notification-list-section"><div class="section-heading"><div><h2>Activity inbox</h2><p>Operational notices from this workspace</p></div></div><div v-for="item in visibleNotifications" :key="item.id" class="notification-row" :class="{ 'notification-unread': !item.is_read && !item.read_at }"><div class="notification-icon" :class="item.notification_type === 'deadline' ? 'notification-icon-danger' : item.notification_type === 'overlap' ? 'notification-icon-caution' : ''"><CalendarClock v-if="item.notification_type === 'deadline'" :size="18" /><GitCompare v-else-if="item.notification_type === 'overlap'" :size="18" /><Activity v-else :size="18" /></div><div class="notification-copy"><div class="notification-title-line"><strong>{{ item.title }}</strong><span>{{ dateTime(item.created_at) }}</span></div><p>{{ item.message }}</p><button v-if="item.related_complaint_id" class="inline-link" @click="navigateToComplaint(item.related_complaint_id)">Open case <ArrowRight :size="13" /></button></div><button v-if="!item.is_read && !item.read_at" class="button button-quiet button-small" @click="markRead(item)"><Check :size="14" /> Mark read</button><span v-else class="read-state">Read</span></div><div v-if="!visibleNotifications.length" class="empty-state-block"><CheckCircle2 :size="24" /><strong>You're all caught up</strong><p>No notifications match this view.</p></div></section>
    </template>

    <!-- IMPORTS -->
    <template v-else-if="page === 'imports'">
      <div class="import-layout"><section class="content-section import-main"><div class="section-heading"><div><h2>Import complaint records</h2><p>Upload a CSV, check the rows, then confirm the import.</p></div></div><div class="import-dropzone" :class="{ 'import-file-loaded': selectedFile }"><input id="complaint-csv-file" type="file" accept=".csv,text/csv" aria-label="Choose CSV file" @change="onFilePicked" /><div class="import-upload-icon"><FileSpreadsheet :size="24" /></div><strong>{{ selectedFile ? selectedFile.name : 'Choose a CSV file' }}</strong><p>{{ selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB · Ready to preview` : 'CSV format · Keep identifiers and column headings intact' }}</p><label class="button button-quiet" for="complaint-csv-file">Browse files</label><span class="import-supported">Files are validated before any records are committed.</span></div><div class="import-action-row"><button class="text-action" @click="downloadTemplate"><Download :size="15" /> Download CSV template</button><button class="button button-primary" :disabled="!selectedFile" @click="previewImport"><FileSearch :size="16" /> Validate file</button></div><div v-if="importPreview" class="import-preview"><div class="import-preview-header"><div><CheckCircle2 v-if="importPreview.is_valid" :size="19" /><AlertCircle v-else :size="19" /><strong>{{ importPreview.local_demo ? 'Local preview complete' : 'Import validation result' }}</strong></div><span class="status-label" :class="importPreview.is_valid ? 'status-good' : 'status-critical'"><i></i>{{ importPreview.is_valid ? 'Ready to review' : 'Needs corrections' }}</span></div><div class="import-counts"><div><span>Rows found</span><strong>{{ importPreview.total_rows ?? importPreview.total_count ?? 0 }}</strong></div><div><span>Valid rows</span><strong>{{ importPreview.success_rows ?? importPreview.valid_rows?.length ?? 0 }}</strong></div><div><span>Errors</span><strong>{{ importPreview.failed_rows ?? importPreview.errors?.length ?? 0 }}</strong></div></div><p v-if="importPreview.local_demo" class="form-hint">This is a basic local preview. Start the Flask API for authoritative field-level validation and commit.</p><button class="button button-primary" :disabled="!importPreview.is_valid" @click="commitImport">Confirm import <ArrowRight :size="15" /></button></div></section><aside class="content-section import-guide"><div class="section-heading"><div><h2>Before you import</h2><p>Keep the register consistent</p></div></div><ol class="import-steps"><li><span>1</span><div><strong>Use the template</strong><p>Keep column headings unchanged so the importer can map fields correctly.</p></div></li><li><span>2</span><div><strong>Check institution IDs</strong><p>Use a Permanent ID already present in the institution directory.</p></div></li><li><span>3</span><div><strong>Review the preview</strong><p>Resolve validation errors before confirming any changes.</p></div></li></ol><div class="import-safety"><ShieldCheck :size="17" /><span>Only import data you are authorized to process. Use fictional records for demonstrations.</span></div></aside></div><section v-if="importHistory.length" class="content-section import-history"><div class="section-heading"><div><h2>Recent imports</h2><p>Latest completed and attempted batches</p></div></div><div class="table-wrap"><table class="data-table"><thead><tr><th>File</th><th>Status</th><th>Rows processed</th><th>Created by</th><th>Date</th></tr></thead><tbody><tr v-for="batch in importHistory" :key="batch.id"><td><strong>{{ batch.filename }}</strong></td><td><span class="status-label" :class="statusClass(batch.status)"><i></i>{{ batch.status }}</span></td><td>{{ batch.success_rows }} / {{ batch.total_rows }}</td><td>{{ batch.created_by_name }}</td><td>{{ shortDate(batch.created_at) }}</td></tr></tbody></table></div></section>
    </template>

    <!-- ADMINISTRATION -->
    <template v-else-if="page === 'admin'">
      <div class="admin-status-row">
        <section class="content-section system-status-panel">
          <div class="system-status-title">
            <span class="system-status-icon"><Activity :size="19" /></span>
            <div>
              <h2>System status</h2>
              <p>Authoritative connectivity and platform status</p>
            </div>
          </div>
          <div class="system-status-grid">
            <div>
              <span>API service</span>
              <strong><i :class="ui.isDemoMode ? 'led-warn' : 'led-good'"></i>{{ ui.isDemoMode ? 'Not reachable' : 'Responding' }}</strong>
            </div>
            <div>
              <span>PostgreSQL Database</span>
              <strong><i :class="systemStatus?.database?.toLowerCase().includes('healthy') ? 'led-good' : 'led-warn'"></i>{{ systemStatus?.database || 'Connected' }}</strong>
            </div>
            <div>
              <span>Platform Version</span>
              <strong>{{ systemStatus?.portal_version || 'AICTE-CMP v2.0' }}</strong>
            </div>
          </div>
          <button class="button button-quiet button-small" @click="loadWorkspace"><RefreshCw :size="14" /> Refresh health</button>
        </section>

        <section class="content-section admin-note-panel">
          <ShieldCheck :size="20" />
          <h2>Three-tier access model</h2>
          <p>Access control is strictly enforced in Python/Flask at the API layer. System Admin governs the platform; Industries manage complaints across all departments; Citizens register and track their tickets.</p>
        </section>
      </div>

      <!-- System Accounts Management -->
      <section class="content-section admin-users-section">
        <div class="section-heading table-title-row">
          <div>
            <h2>Platform accounts & credentials</h2>
            <p>{{ filteredAdminUsers.length }} accounts matching current filter criteria</p>
          </div>
          <button class="button button-primary button-small" @click="openCreateIndustryModal">
            <UserPlus :size="15" /> Create Industry Account
          </button>
        </div>

        <div class="filter-bar" style="margin-bottom: 12px; border: none; padding: 0;">
          <div class="segmented-filter" role="group" aria-label="Role filter">
            <button :class="{ selected: userRoleFilter === 'ALL' }" @click="userRoleFilter = 'ALL'">
              All accounts ({{ adminUsers.length }})
            </button>
            <button :class="{ selected: userRoleFilter === 'INDUSTRY' }" @click="userRoleFilter = 'INDUSTRY'">
              Industry ({{ adminUsers.filter((u: Row) => ['INDUSTRY', 'OFFICER'].includes(String(u.role).toUpperCase())).length }})
            </button>
            <button :class="{ selected: userRoleFilter === 'SYSTEM_ADMIN' }" @click="userRoleFilter = 'SYSTEM_ADMIN'">
              System Admin ({{ adminUsers.filter((u: Row) => ['SYSTEM_ADMIN', 'ADMIN'].includes(String(u.role).toUpperCase())).length }})
            </button>
            <button :class="{ selected: userRoleFilter === 'USER' }" @click="userRoleFilter = 'USER'">
              Complainants ({{ adminUsers.filter((u: Row) => String(u.role).toUpperCase() === 'USER').length }})
            </button>
          </div>
        </div>

        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Official Email</th>
                <th>Canonical Role</th>
                <th>Department / Bureau</th>
                <th>Account Status</th>
                <th>Credentials</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredAdminUsers" :key="user.id">
                <td>
                  <div class="user-table-cell">
                    <span class="user-table-avatar">{{ (user.name || 'U').split(' ').map((x: string) => x[0]).join('').slice(0,2) }}</span>
                    <div>
                      <strong>{{ user.name }}</strong>
                      <small style="display: block; color: var(--muted); font-size: 12px;">{{ user.designation || 'Staff Officer' }}</small>
                    </div>
                  </div>
                </td>
                <td><span style="font-family: 'IBM Plex Mono', monospace; font-size: 12px;">{{ user.email }}</span></td>
                <td>
                  <span
                    class="status-label"
                    :class="String(user.role).toUpperCase().includes('ADMIN') ? 'status-critical' : String(user.role).toUpperCase().includes('INDUSTRY') || String(user.role).toUpperCase().includes('OFFICER') ? 'status-pending' : 'status-good'"
                  >
                    <i></i>{{ String(user.role || '').toUpperCase() }}
                  </span>
                </td>
                <td><span class="bureau-tag">{{ user.bureau_name || user.bureau_code || 'All Bureaus' }}</span></td>
                <td>
                  <button
                    class="button button-quiet button-small"
                    style="min-height: 26px; padding: 0 8px; font-size: 12px;"
                    :title="user.is_active ? 'Click to disable account' : 'Click to enable account'"
                    @click="toggleUserStatus(user)"
                  >
                    <span class="status-label" :class="user.is_active ? 'status-good' : 'status-critical'" style="padding: 0; background: transparent; border: none;">
                      <i></i>{{ user.is_active ? 'Active' : 'Disabled' }}
                    </span>
                  </button>
                </td>
                <td>
                  <button class="button button-quiet button-small" @click="openResetPassword(user)">
                    <KeyRound :size="13" /> Reset password
                  </button>
                </td>
              </tr>
              <tr v-if="!filteredAdminUsers.length">
                <td colspan="6" class="empty-cell">No accounts found in this role.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- All Industries / Departments Directory -->
      <section class="content-section admin-industries-section" style="margin-top: 20px;">
        <div class="section-heading table-title-row">
          <div>
            <h2>All industries & departments</h2>
            <p>Bureaus, cell heads and current grievance workload</p>
          </div>
          <span class="subtle-note">{{ adminIndustries.length }} departments registered</span>
        </div>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Bureau Code</th>
                <th>Department / Bureau Name</th>
                <th>Assigned Head / Lead</th>
                <th>Caseworkers</th>
                <th>Total Grievances</th>
                <th>Active Cases</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="bureau in adminIndustries" :key="bureau.id">
                <td><span class="bureau-tag">{{ bureau.code }}</span></td>
                <td><strong>{{ bureau.name }}</strong></td>
                <td>{{ bureau.lead || 'Bureau Director' }}</td>
                <td><strong>{{ bureau.users_count || 1 }}</strong></td>
                <td>{{ bureau.total_complaints || complaints.filter((c: Row) => (c.current_bureau_code || c.receiving_bureau_code) === bureau.code).length }}</td>
                <td>
                  <span class="open-count">
                    {{ bureau.open_complaints || complaints.filter((c: Row) => (c.current_bureau_code || c.receiving_bureau_code) === bureau.code && !['Disposed', 'Closed'].includes(c.status)).length }}
                  </span>
                </td>
                <td>
                  <button class="button button-quiet button-small" @click="bureauFilter = bureau.code; router.push('/complaints')">
                    View complaints <ChevronRight :size="13" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- System Settings & Grievance Categories -->
      <div class="lower-grid" style="margin-top: 20px;">
        <section class="content-section admin-sla-section">
          <div class="section-heading">
            <div>
              <h2>Statutory resolution timelines (SLAs)</h2>
              <p>Platform default service level agreements</p>
            </div>
            <Sliders :size="16" style="color: var(--muted);" />
          </div>
          <div style="padding: 12px 18px 18px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
              <div style="padding: 12px; border-radius: 6px; background: var(--canvas); border: 1px solid var(--line);">
                <div style="font-size: 12px; color: var(--critical); font-weight: 700; text-transform: uppercase;">Critical Priority</div>
                <div style="font-size: 20px; font-weight: 700; margin-top: 4px; font-family: 'IBM Plex Mono', monospace;">{{ adminSettings.sla_days?.Critical || 7 }} <small style="font-size: 12px; font-weight: 500;">Days</small></div>
                <div style="font-size: 12px; color: var(--muted); margin-top: 4px;">Immediate safety & compliance</div>
              </div>
              <div style="padding: 12px; border-radius: 6px; background: var(--canvas); border: 1px solid var(--line);">
                <div style="font-size: 12px; color: var(--caution); font-weight: 700; text-transform: uppercase;">High Priority</div>
                <div style="font-size: 20px; font-weight: 700; margin-top: 4px; font-family: 'IBM Plex Mono', monospace;">{{ adminSettings.sla_days?.High || 15 }} <small style="font-size: 12px; font-weight: 500;">Days</small></div>
                <div style="font-size: 12px; color: var(--muted); margin-top: 4px;">Institutional fee & admission</div>
              </div>
              <div style="padding: 12px; border-radius: 6px; background: var(--canvas); border: 1px solid var(--line);">
                <div style="font-size: 12px; color: var(--primary); font-weight: 700; text-transform: uppercase;">Medium Priority</div>
                <div style="font-size: 20px; font-weight: 700; margin-top: 4px; font-family: 'IBM Plex Mono', monospace;">{{ adminSettings.sla_days?.Medium || 30 }} <small style="font-size: 12px; font-weight: 500;">Days</small></div>
                <div style="font-size: 12px; color: var(--muted); margin-top: 4px;">General grievances & queries</div>
              </div>
              <div style="padding: 12px; border-radius: 6px; background: var(--canvas); border: 1px solid var(--line);">
                <div style="font-size: 12px; color: var(--muted); font-weight: 700; text-transform: uppercase;">Low Priority</div>
                <div style="font-size: 20px; font-weight: 700; margin-top: 4px; font-family: 'IBM Plex Mono', monospace;">{{ adminSettings.sla_days?.Low || 45 }} <small style="font-size: 12px; font-weight: 500;">Days</small></div>
                <div style="font-size: 12px; color: var(--muted); margin-top: 4px;">Informational submissions</div>
              </div>
            </div>
            <div style="padding: 12px; border-radius: 6px; background: var(--canvas); border: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between;">
              <div>
                <strong style="font-size: 12px; display: block;">Cross-Industry Overlap Engine</strong>
                <span style="font-size: 12px; color: var(--muted);">Sensitivity threshold: {{ Math.round((adminSettings.overlap_threshold || 0.65) * 100) }}% (TF-IDF + Entity Matching)</span>
              </div>
              <span class="status-label status-good"><i></i>Active</span>
            </div>
          </div>
        </section>

        <!-- Complaint Categories Manager -->
        <section class="content-section admin-categories-section">
          <div class="section-heading">
            <div>
              <h2>Grievance categories</h2>
              <p>Taxonomy for complaint filing and routing</p>
            </div>
            <span class="subtle-note">{{ (adminSettings.categories || []).length }} categories</span>
          </div>
          <div style="padding: 14px 18px 18px;">
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
              <span
                v-for="cat in adminSettings.categories"
                :key="cat"
                style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px; background: var(--canvas); border: 1px solid var(--line); font-size: 12px;"
              >
                <span>{{ cat }}</span>
                <button
                  type="button"
                  style="border: none; background: transparent; cursor: pointer; color: var(--muted); padding: 0; display: grid; place-items: center;"
                  title="Remove category"
                  @click="removeCategory(cat)"
                >
                  <X :size="12" />
                </button>
              </span>
            </div>

            <form @submit.prevent="addCategory" style="display: flex; gap: 8px;">
              <input
                v-model="newCategoryInput"
                class="form-control"
                placeholder="New category name (e.g. Hostels & Mess)"
                style="flex: 1;"
                required
              />
              <button type="submit" class="button button-primary button-small" style="flex: none;">
                <Plus :size="14" /> Add category
              </button>
            </form>
          </div>
        </section>
      </div>

      <!-- Audit Activity Log -->
      <section class="content-section admin-audit-section" style="margin-top: 20px;">
        <div class="section-heading">
          <div>
            <h2>Recent audit activity</h2>
            <p>Authoritative log of administrative, assignment, and status modifications</p>
          </div>
        </div>
        <div v-if="auditLogs.length" class="audit-list">
          <div v-for="log in auditLogs.slice(0, 10)" :key="log.id" class="audit-row">
            <div class="audit-icon"><ClipboardCheck :size="16" /></div>
            <div>
              <strong>{{ log.action || log.action_type || 'Recorded action' }}</strong>
              <p>{{ log.description || log.entity_type || 'Administrative event' }}</p>
            </div>
            <span>{{ dateTime(log.created_at) }}</span>
          </div>
        </div>
        <div v-else class="quiet-empty">
          <Database :size="18" />
          <span>{{ ui.isDemoMode ? 'Audit events are not available while running in local demo mode.' : 'No audit events recorded yet.' }}</span>
        </div>
      </section>
    </template>
  </div>

  <!-- New complaint drawer -->
  <Transition name="drawer">
    <div v-if="newComplaintOpen" class="modal-backdrop" @click.self="newComplaintOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true" aria-labelledby="new-complaint-title">
        <div class="drawer-header"><div><h2 id="new-complaint-title">Register a complaint</h2><p>Create a case in the centralized register.</p></div><button class="icon-button" aria-label="Close form" @click="newComplaintOpen = false"><X :size="19" /></button></div>
        <form class="new-complaint-form" @submit.prevent="submitNewComplaint">
          <label class="field-label" for="new-subject">Complaint subject <span>*</span></label><input id="new-subject" v-model="newForm.subject" class="form-control" required maxlength="180" placeholder="State the issue in one line" />
          <label class="field-label" for="new-institution">Institution <span>*</span></label><select id="new-institution" v-model="newForm.institution_id" class="form-control" required><option v-for="institution in institutions" :key="institution.id" :value="String(institution.id)">{{ institution.name }}</option></select>
          <label class="field-label" for="new-description">Complaint description <span>*</span></label><textarea id="new-description" v-model="newForm.description" class="form-control form-textarea" required rows="5" placeholder="Summarize the report and the action requested."></textarea>
          <div class="form-two-column"><div><label class="field-label" for="new-category">Category</label><select id="new-category" v-model="newForm.category" class="form-control"><option>General administration</option><option>Fee irregularity</option><option>Admission irregularity</option><option>Faculty compliance</option><option>Infrastructure</option><option>Student safety</option><option>Financial records</option><option>Approval compliance</option></select></div><div><label class="field-label" for="new-priority">Priority</label><select id="new-priority" v-model="newForm.priority" class="form-control"><option>Low</option><option>Medium</option><option>High</option><option>Critical</option></select></div></div>
          <label class="field-label" for="new-bureau">Receiving Bureau / Cell</label><select id="new-bureau" v-model="newForm.bureau_id" class="form-control"><option v-for="bureau in bureaus" :key="bureau.id" :value="String(bureau.id)">{{ bureau.code }}: {{ bureau.name }}</option></select>
          <label class="field-label" for="new-due-date">Target due date</label><input id="new-due-date" v-model="newForm.due_at" class="form-control" type="date" />
          <div class="form-drawer-footer"><button type="button" class="button button-quiet" @click="newComplaintOpen = false">Cancel</button><button type="submit" class="button button-primary"><Check :size="16" /> Save complaint</button></div>
        </form>
      </section>
    </div>
  </Transition>

  <!-- Overlap comparison drawer (Human Verification Workflow) -->
  <Transition name="drawer">
    <div v-if="selectedOverlap" class="modal-backdrop" @click.self="selectedOverlap = null">
      <section class="form-drawer comparison-drawer" role="dialog" aria-modal="true" aria-labelledby="overlap-review-title">
        <div class="drawer-header">
          <div>
            <h2 id="overlap-review-title">Side-by-Side Overlap Verification</h2>
            <p>Verify whether potential overlap requires multi-bureau linking and coordination. Cases remain independent with unique IDs.</p>
          </div>
          <button class="icon-button" aria-label="Close review" @click="selectedOverlap = null"><X :size="19" /></button>
        </div>

        <div class="review-explanation">
          <div class="review-score-large">{{ Math.round((selectedOverlap.match_score || 0) * 100) }}<small>%</small></div>
          <div>
            <strong>{{ selectedOverlap.match_method || 'Identifier + Entity Matching Signal' }}</strong>
            <p>{{ selectedOverlap.match_reason }}</p>
          </div>
        </div>

        <!-- Side-by-Side Comparison Grid -->
        <div class="compare-records">
          <!-- Case A -->
          <article>
            <div class="compare-label">
              <span class="case-id">{{ getCaseForLink(selectedOverlap, 'a').case_number }}</span>
              <span class="bureau-tag">{{ getCaseForLink(selectedOverlap, 'a').bureau_code || 'Bureau A' }}</span>
            </div>
            <h3>{{ getCaseForLink(selectedOverlap, 'a').subject }}</h3>
            <p class="[text-wrap:pretty]">{{ getCaseForLink(selectedOverlap, 'a').description }}</p>

            <dl>
              <div>
                <dt>Institution</dt>
                <dd>{{ getCaseForLink(selectedOverlap, 'a').institution_name || 'AICTE Institution' }}</dd>
              </div>
              <div>
                <dt>Permanent ID</dt>
                <dd><strong class="font-mono text-primary">{{ getCaseForLink(selectedOverlap, 'a').institution_code || '1-XXXXXXXX' }}</strong></dd>
              </div>
              <div>
                <dt>Category</dt>
                <dd>{{ getCaseForLink(selectedOverlap, 'a').category }}</dd>
              </div>
              <div>
                <dt>Current Status</dt>
                <dd>{{ getCaseForLink(selectedOverlap, 'a').status || 'Unknown' }}</dd>
              </div>
            </dl>

            <button class="text-action" @click="navigateToComplaint(getCaseForLink(selectedOverlap, 'a').id); selectedOverlap = null">
              Open Full Case A <ArrowUpRight :size="14" />
            </button>
          </article>

          <!-- Case B -->
          <article>
            <div class="compare-label">
              <span class="case-id">{{ getCaseForLink(selectedOverlap, 'b').case_number }}</span>
              <span class="bureau-tag">{{ getCaseForLink(selectedOverlap, 'b').bureau_code || 'Bureau B' }}</span>
            </div>
            <h3>{{ getCaseForLink(selectedOverlap, 'b').subject }}</h3>
            <p class="[text-wrap:pretty]">{{ getCaseForLink(selectedOverlap, 'b').description }}</p>

            <dl>
              <div>
                <dt>Institution</dt>
                <dd>{{ getCaseForLink(selectedOverlap, 'b').institution_name || 'AICTE Institution' }}</dd>
              </div>
              <div>
                <dt>Permanent ID</dt>
                <dd><strong class="font-mono text-primary">{{ getCaseForLink(selectedOverlap, 'b').institution_code || '1-XXXXXXXX' }}</strong></dd>
              </div>
              <div>
                <dt>Category</dt>
                <dd>{{ getCaseForLink(selectedOverlap, 'b').category }}</dd>
              </div>
              <div>
                <dt>Current Status</dt>
                <dd>{{ getCaseForLink(selectedOverlap, 'b').status || 'Unknown' }}</dd>
              </div>
            </dl>

            <button class="text-action" @click="navigateToComplaint(getCaseForLink(selectedOverlap, 'b').id); selectedOverlap = null">
              Open Full Case B <ArrowUpRight :size="14" />
            </button>
          </article>
        </div>

        <!-- Verification Remarks Input -->
        <div style="padding: 12px 18px 0;">
          <label class="field-label" for="overlap-remarks">Officer Verification Remarks</label>
          <input
            id="overlap-remarks"
            v-model="overlapReviewRemarks"
            class="form-control"
            placeholder="Record review notes, cross-bureau coordination reasons, or false alert rationale..."
          />
        </div>

        <div class="review-human-note">
          <ShieldCheck :size="17" />
          <span>Full workflow: Confirmed Overlap links records, notifies handling bureaus, and logs coordination history without auto-merging.</span>
        </div>

        <div class="form-drawer-footer review-actions">
          <button class="button button-quiet" :disabled="isReviewing" @click="reviewOverlap(selectedOverlap, 'Needs Review')">
            <Clock3 :size="15" /> Needs Review
          </button>
          <button class="button button-outline-danger" :disabled="isReviewing" @click="reviewOverlap(selectedOverlap, 'False Alert')">
            <X :size="15" /> False Alert
          </button>
          <button class="button button-primary" :disabled="isReviewing" @click="reviewOverlap(selectedOverlap, 'Confirmed Overlap')">
            <Check :size="16" /> Confirmed Overlap
          </button>
        </div>
      </section>
    </div>
  </Transition>

  <!-- Next Action Modal -->
  <Transition name="drawer">
    <div v-if="isNextActionOpen" class="modal-backdrop" @click.self="isNextActionOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true">
        <div class="drawer-header">
          <div><h2>Update Next Action Required</h2><p>Specify immediate operational next step, deadline and responsible caseworker.</p></div>
          <button class="icon-button" @click="isNextActionOpen = false"><X :size="18" /></button>
        </div>
        <form class="new-complaint-form" @submit.prevent="submitNextAction">
          <label class="field-label" for="na-desc">Required Next Action <span>*</span></label>
          <textarea id="na-desc" v-model="nextActionText" class="form-control form-textarea" rows="3" required placeholder="e.g. Issue show-cause notice regarding capitation fee collection..."></textarea>
          <div class="form-two-column">
            <div>
              <label class="field-label" for="na-due">Target Completion Date</label>
              <input id="na-due" v-model="nextActionDueDate" type="date" class="form-control" />
            </div>
            <div>
              <label class="field-label" for="na-who">Responsible Assignee / Bureau</label>
              <input id="na-who" v-model="nextActionAssignee" class="form-control" placeholder="e.g. Smt. Ananya Sen (PGRC)" />
            </div>
          </div>
          <div class="form-drawer-footer">
            <button type="button" class="button button-quiet" @click="isNextActionOpen = false">Cancel</button>
            <button type="submit" class="button button-primary"><Check :size="15" /> Save Next Action</button>
          </div>
        </form>
      </section>
    </div>
  </Transition>

  <!-- Coordination Note Modal -->
  <Transition name="drawer">
    <div v-if="isCoordinationNoteOpen" class="modal-backdrop" @click.self="isCoordinationNoteOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true">
        <div class="drawer-header">
          <div><h2>Add Cross-Bureau Coordination Note</h2><p>Document agreed actions between Bureaus to avoid conflicting decisions.</p></div>
          <button class="icon-button" @click="isCoordinationNoteOpen = false"><X :size="18" /></button>
        </div>
        <form class="new-complaint-form" @submit.prevent="submitCoordinationNote">
          <label class="field-label" for="coord-text">Agreed Bureau Decisions & Remarks <span>*</span></label>
          <textarea id="coord-text" v-model="coordinationNoteText" class="form-control form-textarea" rows="4" required placeholder="Document joint inspection consensus, committee decisions, or cross-cell agreements..."></textarea>
          <div class="form-drawer-footer">
            <button type="button" class="button button-quiet" @click="isCoordinationNoteOpen = false">Cancel</button>
            <button type="submit" class="button button-primary"><Check :size="15" /> Record Note</button>
          </div>
        </form>
      </section>
    </div>
  </Transition>

  <!-- Query Complainant Modal -->
  <Transition name="drawer">
    <div v-if="isRequestInfoOpen" class="modal-backdrop" @click.self="isRequestInfoOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true">
        <div class="drawer-header">
          <div><h2>Request Clarification from Complainant</h2><p>Send an official query. Complainant can respond without filing a new complaint.</p></div>
          <button class="icon-button" @click="isRequestInfoOpen = false"><X :size="18" /></button>
        </div>
        <form class="new-complaint-form" @submit.prevent="submitRequestInfo">
          <label class="field-label" for="query-msg">Official Query / Missing Information <span>*</span></label>
          <textarea id="query-msg" v-model="requestInfoQuery" class="form-control form-textarea" rows="4" required placeholder="State clearly what receipts, semester fee records, or clarifications are required..."></textarea>
          <div class="form-drawer-footer">
            <button type="button" class="button button-quiet" @click="isRequestInfoOpen = false">Cancel</button>
            <button type="submit" class="button button-primary"><Search :size="15" /> Send Query to Complainant</button>
          </div>
        </form>
      </section>
    </div>
  </Transition>

  <!-- Transfer Case Modal -->
  <Transition name="drawer">
    <div v-if="isTransferOpen" class="modal-backdrop" @click.self="isTransferOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true">
        <div class="drawer-header">
          <div><h2>Transfer Complaint to Competent Bureau</h2><p>Transfer procedural jurisdiction without merging or deleting history.</p></div>
          <button class="icon-button" @click="isTransferOpen = false"><X :size="18" /></button>
        </div>
        <form class="new-complaint-form" @submit.prevent="submitTransfer">
          <label class="field-label" for="target-bureau">Target AICTE Bureau / Cell <span>*</span></label>
          <select id="target-bureau" v-model="transferBureauId" class="form-control" required>
            <option v-for="b in bureaus" :key="b.id" :value="String(b.id)">{{ b.code }}: {{ b.name }}</option>
          </select>
          <label class="field-label" for="transfer-remarks">Reason for Transfer <span>*</span></label>
          <textarea id="transfer-remarks" v-model="transferReason" class="form-control form-textarea" rows="3" required placeholder="Specify why the target bureau has statutory jurisdiction..."></textarea>
          <div class="form-drawer-footer">
            <button type="button" class="button button-quiet" @click="isTransferOpen = false">Cancel</button>
            <button type="submit" class="button button-primary"><Layers3 :size="15" /> Confirm Transfer</button>
          </div>
        </form>
      </section>
    </div>
  </Transition>

  <!-- Escalate Case Modal -->
  <Transition name="drawer">
    <div v-if="isEscalateOpen" class="modal-backdrop" @click.self="isEscalateOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true">
        <div class="drawer-header">
          <div><h2>Escalate Complaint to Senior Authority</h2><p>Flag delayed, repeated, or high-risk institutional cases.</p></div>
          <button class="icon-button" @click="isEscalateOpen = false"><X :size="18" /></button>
        </div>
        <form class="new-complaint-form" @submit.prevent="submitEscalate">
          <label class="field-label" for="esc-reason">Escalation Justification <span>*</span></label>
          <textarea id="esc-reason" v-model="escalateReason" class="form-control form-textarea" rows="3" required placeholder="e.g. Repeated non-compliance from institution administration despite statutory reminders..."></textarea>
          <div class="form-drawer-footer">
            <button type="button" class="button button-quiet" @click="isEscalateOpen = false">Cancel</button>
            <button type="submit" class="button button-primary"><CircleAlert :size="15" /> Confirm Escalation</button>
          </div>
        </form>
      </section>
    </div>
  </Transition>

  <!-- Link Case Modal -->
  <Transition name="drawer">
    <div v-if="isLinkCaseOpen" class="modal-backdrop" @click.self="isLinkCaseOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true">
        <div class="drawer-header">
          <div><h2>Link Related Complaint</h2><p>Link two related cases while keeping their IDs, owners and histories intact.</p></div>
          <button class="icon-button" @click="isLinkCaseOpen = false"><X :size="18" /></button>
        </div>
        <form class="new-complaint-form" @submit.prevent="submitLinkCase">
          <label class="field-label" for="link-target">Target Ticket or Case Number <span>*</span></label>
          <input id="link-target" v-model="linkCaseNumber" class="form-control" required placeholder="e.g. AICTE-2026-AB-0102 or AICTE-2026-X1Y2Z3" />
          <label class="field-label" for="link-notes">Coordination / Relationship Notes</label>
          <textarea id="link-notes" v-model="linkCaseNotes" class="form-control form-textarea" rows="2" placeholder="Describe relation (e.g. Same faculty cohort, connected capitation grievance)..."></textarea>
          <div class="form-drawer-footer">
            <button type="button" class="button button-quiet" @click="isLinkCaseOpen = false">Cancel</button>
            <button type="submit" class="button button-primary"><GitCompare :size="15" /> Link Case</button>
          </div>
        </form>
      </section>
    </div>
  </Transition>

  <!-- Reassign Case Modal -->
  <Transition name="drawer">
    <div v-if="isReassignOpen" class="modal-backdrop" @click.self="isReassignOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true">
        <div class="drawer-header">
          <div><h2>Reassign Case Officer</h2><p>Allocate responsibility to another authorized officer.</p></div>
          <button class="icon-button" @click="isReassignOpen = false"><X :size="18" /></button>
        </div>
        <form class="new-complaint-form" @submit.prevent="submitReassign">
          <label class="field-label" for="reassign-officer">Select Responsible Officer <span>*</span></label>
          <select id="reassign-officer" v-model="reassignOfficerId" class="form-control" required>
            <option value="">Choose officer...</option>
            <option v-for="u in adminUsers.filter((x: Row) => ['INDUSTRY', 'OFFICER'].includes(String(x.role).toUpperCase()))" :key="u.id" :value="String(u.id)">
              {{ u.name }} ({{ u.email }})
            </option>
          </select>
          <div class="form-drawer-footer">
            <button type="button" class="button button-quiet" @click="isReassignOpen = false">Cancel</button>
            <button type="submit" class="button button-primary"><Users :size="15" /> Reassign</button>
          </div>
        </form>
      </section>
    </div>
  </Transition>

  <!-- Create Industry Account drawer -->
  <Transition name="drawer">
    <div v-if="isCreateIndustryOpen" class="modal-backdrop" @click.self="isCreateIndustryOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true" aria-labelledby="create-industry-title">
        <div class="drawer-header">
          <div>
            <h2 id="create-industry-title">Create Industry Account</h2>
            <p>Provision credentials for a departmental caseworker or bureau coordinator.</p>
          </div>
          <button class="icon-button" aria-label="Close form" @click="isCreateIndustryOpen = false"><X :size="19" /></button>
        </div>
        <form class="new-complaint-form" @submit.prevent="submitCreateIndustry">
          <label class="field-label" for="ind-name">Full Name <span>*</span></label>
          <input id="ind-name" v-model="newIndustryUser.name" class="form-control" required placeholder="e.g. Smt. Neha Verma" />

          <label class="field-label" for="ind-email">Official Email <span>*</span></label>
          <input id="ind-email" v-model="newIndustryUser.email" type="email" class="form-control" required placeholder="e.g. officer.ab@aicte.gov.in" />

          <label class="field-label" for="ind-bureau">Assigned Department / Bureau <span>*</span></label>
          <select id="ind-bureau" v-model="newIndustryUser.bureau_id" class="form-control" required>
            <option v-for="bureau in bureaus" :key="bureau.id" :value="String(bureau.id)">{{ bureau.code }}: {{ bureau.name }}</option>
          </select>

          <label class="field-label" for="ind-designation">Designation / Role Title <span>*</span></label>
          <input id="ind-designation" v-model="newIndustryUser.designation" class="form-control" required placeholder="e.g. Senior Caseworker" />

          <label class="field-label" for="ind-pwd">Initial Password <span>*</span></label>
          <input id="ind-pwd" v-model="newIndustryUser.password" type="password" class="form-control" required minlength="6" placeholder="Minimum 6 characters" />

          <div class="form-drawer-footer">
            <button type="button" class="button button-quiet" @click="isCreateIndustryOpen = false">Cancel</button>
            <button type="submit" class="button button-primary"><UserPlus :size="16" /> Provision Account</button>
          </div>
        </form>
      </section>
    </div>
  </Transition>

  <!-- Reset User Password drawer -->
  <Transition name="drawer">
    <div v-if="isResetPasswordOpen && selectedResetUser" class="modal-backdrop" @click.self="isResetPasswordOpen = false">
      <section class="form-drawer" role="dialog" aria-modal="true" aria-labelledby="reset-password-title">
        <div class="drawer-header">
          <div>
            <h2 id="reset-password-title">Reset User Credentials</h2>
            <p>Update credentials for {{ selectedResetUser.name }}</p>
          </div>
          <button class="icon-button" aria-label="Close form" @click="isResetPasswordOpen = false"><X :size="19" /></button>
        </div>
        <form class="new-complaint-form" @submit.prevent="submitResetPassword">
          <div style="margin-top: 16px; padding: 12px; border-radius: 6px; background: var(--canvas); border: 1px solid var(--line);">
            <div style="font-size: 13px; font-weight: 600;">{{ selectedResetUser.name }}</div>
            <div style="font-size: 12px; color: var(--muted); margin-top: 2px;">{{ selectedResetUser.email }}</div>
            <div style="font-size: 12px; margin-top: 6px; display: inline-flex; align-items: center; padding: 2px 6px; border-radius: 4px; background: var(--surface); border: 1px solid var(--line-strong); font-weight: 600;">
              {{ selectedResetUser.role }}
            </div>
          </div>

          <label class="field-label" for="new-pass">New Password <span>*</span></label>
          <input id="new-pass" v-model="newPasswordInput" type="password" class="form-control" required minlength="6" placeholder="Enter new password" />

          <div class="form-drawer-footer">
            <button type="button" class="button button-quiet" @click="isResetPasswordOpen = false">Cancel</button>
            <button type="submit" class="button button-primary"><KeyRound :size="16" /> Save New Password</button>
          </div>
        </form>
      </section>
    </div>
  </Transition>
</template>
