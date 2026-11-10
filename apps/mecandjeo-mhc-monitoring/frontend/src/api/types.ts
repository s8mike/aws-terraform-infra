// Types mirror the backend schemas in app/schemas.py.
// The API returns naive ISO datetimes that are UTC; use parseServerDate() to display them.

export type Role = 'operator' | 'manager' | 'admin'

export interface User {
  id: number
  email: string
  full_name: string
  role: Role
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  full_name: string
  password: string
  role: 'operator'
  is_active: boolean
}

export interface LookupValue {
  code: string
  label: string
  short_key: string | null
}

export interface LookupCrane {
  id: number
  mhc_number: string
}

export interface Lookups {
  nature_of_work: LookupValue[]
  working_area: LookupValue[]
  delay_type: LookupValue[]
  shift_code: LookupValue[]
  cranes: LookupCrane[]
}

export interface Shift {
  id: number
  operator_id: number
  crane_id: number
  mhc_number: string
  shift_code: string | null
  started_at: string
  ended_at: string | null
  status: string
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ShiftStartRequest {
  mhc_number: string
  shift_code: string
  started_at: string
  notes?: string
}

export interface EndRequest {
  ended_at: string
  notes?: string
}

export interface TaskLog {
  id: number
  shift_id: number
  operator_id: number
  crane_id: number
  nature_of_work: string
  working_area: string
  vessel_name: string | null
  bay_reference: string | null
  container_count: number
  started_at: string
  ended_at: string | null
  status: string
  notes: string | null
  created_at: string
  updated_at: string
}

export interface TaskLogStartRequest {
  shift_id: number
  nature_of_work: string
  working_area: string
  vessel_name?: string
  bay_reference?: string
  container_count?: number
  started_at: string
  notes?: string
}

export interface TaskLogEndRequest {
  ended_at: string
  container_count?: number
  notes?: string
}

export interface DelayLog {
  id: number
  task_log_id: number
  delay_type: string
  custom_delay_type: string | null
  started_at: string
  ended_at: string | null
  duration_minutes: number | null
  is_operator_controllable: boolean
  notes: string | null
  created_at: string
  updated_at: string
}

export interface DelayLogStartRequest {
  task_log_id: number
  delay_type: string
  custom_delay_type?: string
  started_at: string
  is_operator_controllable?: boolean
  notes?: string
}

export interface DelayLogEndRequest {
  ended_at: string
  duration_minutes?: number
  notes?: string
}

export interface WorkingConditionRequest {
  shift_id: number
  weather_condition?: string
  visibility?: string
  wind_condition?: string
  deck_condition?: string
  congestion_level?: string
  notes?: string
  recorded_at?: string
}

export interface WorkingCondition extends WorkingConditionRequest {
  id: number
  recorded_at: string
  created_at: string
  updated_at: string
}

export interface OperatorSummary {
  operator_id: number
  total_shifts: number
  active_shift_id: number | null
  completed_tasks: number
  total_container_count: number
  total_delay_minutes: number
}

export interface OperatorActiveState {
  shift: Shift | null
  task: TaskLog | null
  delay: DelayLog | null
}

export interface ManagerDashboard {
  total_operators: number
  total_cranes: number
  active_shifts: number
  active_tasks: number
  active_delays: number
  completed_tasks: number
  total_container_count: number
  total_delay_minutes: number
}

export interface LiveOperatorStatus {
  operator_id: number
  operator_name: string
  shift_id: number
  shift_code: string | null
  mhc_number: string
  crane_id: number
  shift_started_at: string
  active_task_id: number | null
  active_task_nature_of_work: string | null
  active_delay_id: number | null
  active_delay_type: string | null
  status: string
}

export interface ActiveShiftOverview {
  shift_id: number
  operator_id: number
  operator_name: string
  crane_id: number
  mhc_number: string
  shift_code: string | null
  started_at: string
  active_task_count: number
  completed_task_count: number
  active_delay_count: number
  total_container_count: number
}

export interface DelayBreakdownItem {
  delay_type: string
  custom_delay_type: string | null
  delay_count: number
  total_delay_minutes: number
  operator_controllable_count: number
}

export interface PerformanceTrendItem {
  group_by: string
  group_key: string
  label: string
  completed_tasks: number
  total_task_minutes: number
  total_delay_minutes: number
  effective_work_minutes: number
  total_container_count: number
  moves_per_hour: number | null
}

export interface PerformanceReportSummary {
  completed_tasks: number
  total_task_minutes: number
  total_delay_minutes: number
  effective_work_minutes: number
  total_container_count: number
  moves_per_hour: number | null
}

export interface PerformanceReportTaskItem {
  task_log_id: number
  operator_id: number
  operator_name: string
  crane_id: number
  mhc_number: string
  nature_of_work: string
  working_area: string
  vessel_name: string | null
  started_at: string
  ended_at: string
  task_minutes: number
  delay_minutes: number
  delay_reasons: string[]
  effective_work_minutes: number
  container_count: number
  moves_per_hour: number | null
}

export interface PerformanceReportDelayItem {
  delay_type: string
  custom_delay_type: string | null
  delay_count: number
  total_delay_minutes: number
}

export interface PerformanceReport {
  date_from: string | null
  date_to: string | null
  operator_id: number | null
  crane_id: number | null
  nature_of_work: string | null
  summary: PerformanceReportSummary
  tasks: PerformanceReportTaskItem[]
  delay_breakdown: PerformanceReportDelayItem[]
}

export interface ReportExport {
  id: number
  requested_by_id: number
  report_type: string
  file_format: string
  date_from: string | null
  date_to: string | null
  status: string
  file_path: string | null
  created_at: string
  updated_at: string
}

export interface Crane {
  id: number
  code: string
  mhc_number: string
  name: string
  manufacturer: string | null
  model: string | null
  capacity_tonnes: number | null
  location: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CraneInput {
  code: string
  mhc_number: string
  name: string
  manufacturer?: string
  model?: string
  capacity_tonnes?: number
  location?: string
  is_active?: boolean
}

export type CraneUpdate = Partial<CraneInput>

export interface ReferenceData {
  id: number
  category: string
  code: string
  label: string
  short_key: string | null
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ReferenceDataInput {
  category: string
  code: string
  label: string
  short_key?: string
  description?: string
  is_active?: boolean
}

export type ReferenceDataUpdate = Partial<ReferenceDataInput>

export interface AdminUserInput {
  email: string
  full_name: string
  password: string
  role: Role
  is_active?: boolean
}

export type AdminUserUpdate = Partial<AdminUserInput>


// Totals for one shift (the "This shift" cards on the operator screen).
export interface ShiftSummary {
  shift_id: number
  mhc_number: string
  completed_tasks: number
  total_container_count: number
  total_delay_minutes: number
}