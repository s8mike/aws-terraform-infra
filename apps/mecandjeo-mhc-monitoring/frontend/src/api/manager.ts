// Manager API calls: dashboard, live status, delay breakdown, performance trends and reports.
// Managers and admins can call all of these; every filter is optional.
import { apiFetch } from './client'
import type {
  ActiveShiftOverview,
  DelayBreakdownItem,
  LiveOperatorStatus,
  ManagerDashboard,
  PerformanceReport,
  PerformanceTrendItem,
} from './types'

export interface DateFilters {
  date_from?: string
  date_to?: string
}

export interface ReportFilters extends DateFilters {
  crane_id?: number
  nature_of_work?: string
}

// Build "?a=1&b=2" from the filters that have a value; empty values are left out.
export function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') search.set(key, String(value))
  }
  const text = search.toString()
  return text ? `?${text}` : ''
}

// Headline counts for the manager overview cards.
export function fetchDashboard(): Promise<ManagerDashboard> {
  return apiFetch<ManagerDashboard>('/api/manager/dashboard')
}

// One row per operator who is on shift right now.
export function fetchLiveStatus(): Promise<LiveOperatorStatus[]> {
  return apiFetch<LiveOperatorStatus[]>('/api/manager/operators/live-status')
}

// Open shifts with their task and delay counts.
export function fetchActiveShifts(): Promise<ActiveShiftOverview[]> {
  return apiFetch<ActiveShiftOverview[]>('/api/manager/shifts/active')
}

// Delay counts and minutes by reason, for an optional date range.
export function fetchDelayBreakdown(filters: DateFilters): Promise<DelayBreakdownItem[]> {
  return apiFetch<DelayBreakdownItem[]>(`/api/manager/delays/breakdown${buildQuery({ ...filters })}`)
}

// Performance grouped by operator, crane, nature_of_work or date.
export function fetchPerformanceTrends(groupBy: string, filters: DateFilters): Promise<PerformanceTrendItem[]> {
  return apiFetch<PerformanceTrendItem[]>(`/api/manager/performance/trends${buildQuery({ group_by: groupBy, ...filters })}`)
}

// Completed-task report with delay context (JSON for the screen).
export function fetchPerformanceReport(filters: ReportFilters): Promise<PerformanceReport> {
  return apiFetch<PerformanceReport>(`/api/reports/performance${buildQuery({ ...filters })}`)
}

// Same report as CSV; the path is used with downloadCsv() because the download needs the auth header.
export function reportCsvPath(filters: ReportFilters): string {
  return `/api/reports/performance.csv${buildQuery({ ...filters })}`
}