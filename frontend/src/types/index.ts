export interface User {
  id: number
  name: string
  email: string
  role: 'SYSTEM_ADMIN' | 'INDUSTRY' | 'USER' | 'admin' | 'officer' | 'senior_authority' | string

  bureau_id?: number | null
  bureau_code?: string | null
  bureau_name?: string | null
  designation?: string | null
  is_active: boolean
  created_at?: string
  last_login_at?: string | null
}

export interface Bureau {
  id: number
  name: string
  code: string
  description?: string
  is_active: boolean
  created_at?: string
}

export interface Institution {
  id: number
  institution_code: string
  name: string
  aliases: string[]
  institution_type: string
  state: string
  district?: string | null
  address?: string | null
  pincode?: string | null
  website?: string | null
  total_complaints?: number
  open_complaints?: number
  disposed_complaints?: number
  escalated_complaints?: number
  bureaus_involved?: string[]
}

export interface CaseAction {
  id: number
  complaint_id: number
  action_type: string
  description: string
  old_status?: string | null
  new_status?: string | null
  old_bureau_code?: string | null
  new_bureau_code?: string | null
  performed_by_name: string
  performed_by_id?: number | null
  created_at: string
}

export interface CaseLink {
  id: number
  complaint_id_a: number
  complaint_id_b: number
  relationship_type: 'potential_overlap' | 'confirmed_related' | 'unrelated' | 'deferred'
  match_score: number
  match_method: string
  match_reason: string
  evidence: {
    same_institution_id?: boolean
    same_institution_code?: boolean
    same_external_reference?: boolean
    institution_match_score?: number
    category_match?: boolean
    shared_keywords?: string[]
    keyword_jaccard?: number
    text_similarity?: number
    content_score?: number
    cross_bureau?: boolean
    overall_score?: number
  }
  review_status: 'pending' | 'confirmed' | 'dismissed' | 'deferred'
  reviewed_by_name?: string | null
  reviewed_by_id?: number | null
  reviewed_at?: string | null
  review_remarks?: string | null
  created_at: string
  case_a?: {
    id: number
    case_number: string
    subject: string
    description: string
    category: string
    status: string
    priority: string
    bureau_code?: string
    institution_name?: string
    institution_code?: string
  }
  case_b?: {
    id: number
    case_number: string
    subject: string
    description: string
    category: string
    status: string
    priority: string
    bureau_code?: string
    institution_name?: string
    institution_code?: string
  }
  other_case?: {
    id: number
    case_number: string
    subject: string
    description: string
    category: string
    status: string
    priority: string
    bureau_code?: string
    institution_name?: string
    institution_code?: string
  }
}

export interface Complaint {
  id: number
  case_number: string
  external_reference?: string | null
  institution_id: number
  institution_name?: string
  institution_code?: string
  institution_state?: string
  category: string
  subject: string
  description: string
  receiving_bureau_id: number
  receiving_bureau_code?: string
  receiving_bureau_name?: string
  current_bureau_id: number
  current_bureau_code?: string
  current_bureau_name?: string
  assigned_user_id?: number | null
  assigned_officer_name?: string | null
  priority: 'Low' | 'Medium' | 'High' | 'Critical'
  status: 'Received' | 'Under Review' | 'Action Required' | 'Awaiting Response' | 'Escalated' | 'Disposed' | 'Closed'
  is_overdue: boolean
  received_at: string
  due_at?: string | null
  last_action_at?: string | null
  disposed_at?: string | null
  resolution_summary?: string | null
  created_at: string
  actions?: CaseAction[]
  related_links?: CaseLink[]
}

export interface NotificationItem {
  id: number
  user_id?: number | null
  bureau_id?: number | null
  role?: string | null
  notification_type: string
  title: string
  message: string
  related_complaint_id?: number | null
  related_case_number?: string | null
  related_case_link_id?: number | null
  is_read: boolean
  read_at?: string | null
  created_at: string
}

export interface KPIs {
  total_complaints: number
  open_cases: number
  action_required: number
  overdue_cases: number
  escalated_cases: number
  disposed_cases: number
  unreviewed_overlaps: number
}

export interface ImportBatch {
  id: number
  filename: string
  total_rows: number
  success_rows: number
  failed_rows: number
  status: string
  created_by_name: string
  created_at: string
}
