// Operator API calls: lookups, current state, summaries, and the shift, task, delay and condition actions.
// Paths match the backend exactly, including trailing slashes.
import { apiFetch } from './client'
import type {
  DelayLog,
  DelayLogEndRequest,
  DelayLogStartRequest,
  EndRequest,
  Lookups,
  OperatorActiveState,
  OperatorSummary,
  Shift,
  ShiftStartRequest,
  ShiftSummary,
  TaskLog,
  TaskLogEndRequest,
  TaskLogStartRequest,
  WorkingCondition,
  WorkingConditionRequest,
} from './types'

// Dropdown values (work types, areas, delay types, shift codes) and active MHC numbers.
export function fetchLookups(): Promise<Lookups> {
  return apiFetch<Lookups>('/api/lookups')
}

// The open shift, task and delay, so the screen can resume after a reload.
export function fetchActiveState(): Promise<OperatorActiveState> {
  return apiFetch<OperatorActiveState>('/api/operators/me/active')
}

// All-time headline numbers for the signed-in operator.
export function fetchOperatorSummary(): Promise<OperatorSummary> {
  return apiFetch<OperatorSummary>('/api/operators/me/summary')
}

// Headline numbers for one shift (starts at zero when the shift starts).
export function fetchShiftSummary(shiftId: number): Promise<ShiftSummary> {
  return apiFetch<ShiftSummary>(`/api/operators/me/shifts/${shiftId}/summary`)
}

// Begin a shift on an MHC.
export function startShift(payload: ShiftStartRequest): Promise<Shift> {
  return apiFetch<Shift>('/api/shifts/start', { method: 'POST', body: payload })
}

// Close a shift (the API refuses while a task is still open).
export function endShift(shiftId: number, payload: EndRequest): Promise<Shift> {
  return apiFetch<Shift>(`/api/shifts/${shiftId}/end`, { method: 'PATCH', body: payload })
}

// Record weather and deck conditions for the open shift.
export function recordWorkingCondition(payload: WorkingConditionRequest): Promise<WorkingCondition> {
  return apiFetch<WorkingCondition>('/api/working-conditions/', { method: 'POST', body: payload })
}

// Begin a task inside the open shift.
export function startTask(payload: TaskLogStartRequest): Promise<TaskLog> {
  return apiFetch<TaskLog>('/api/task-logs/start', { method: 'POST', body: payload })
}

// Close a task (the API refuses while a delay is still open).
export function endTask(taskId: number, payload: TaskLogEndRequest): Promise<TaskLog> {
  return apiFetch<TaskLog>(`/api/task-logs/${taskId}/end`, { method: 'PATCH', body: payload })
}

// Begin a delay against the open task.
export function startDelay(payload: DelayLogStartRequest): Promise<DelayLog> {
  return apiFetch<DelayLog>('/api/delay-logs/start', { method: 'POST', body: payload })
}

// Close a delay; the API calculates the minutes when none are sent.
export function endDelay(delayId: number, payload: DelayLogEndRequest): Promise<DelayLog> {
  return apiFetch<DelayLog>(`/api/delay-logs/${delayId}/end`, { method: 'PATCH', body: payload })
}