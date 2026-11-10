// Admin API calls: users, cranes and reference data. Every route here is admin-only.
// Paths match the backend exactly, including trailing slashes.
import { apiFetch } from './client'
import type { AdminUserInput, Crane, CraneInput, ReferenceData, ReferenceDataInput, User } from './types'

// Fields an admin can change on a user; send only what changed. A password here resets it.
export interface UserPatch {
  email?: string
  full_name?: string
  password?: string
  role?: string
  is_active?: boolean
}

// Fields an admin can change on a crane; null clears an optional field.
export interface CranePatch {
  code?: string
  mhc_number?: string
  name?: string
  manufacturer?: string | null
  model?: string | null
  capacity_tonnes?: number | null
  location?: string | null
  is_active?: boolean
}

// Fields an admin can change on a reference value; the code itself is never changed.
export interface ReferenceDataPatch {
  label?: string
  short_key?: string | null
  description?: string | null
  is_active?: boolean
}

// All user accounts.
export function listUsers(): Promise<User[]> {
  return apiFetch<User[]>('/api/users/')
}

// Create an account with any role.
export function createUser(payload: AdminUserInput): Promise<User> {
  return apiFetch<User>('/api/admin/users', { method: 'POST', body: payload })
}

// Change an account (name, email, role, password reset, active flag).
export function updateUser(userId: number, patch: UserPatch): Promise<User> {
  return apiFetch<User>(`/api/admin/users/${userId}`, { method: 'PATCH', body: patch })
}

// All cranes, including inactive ones.
export function listCranes(): Promise<Crane[]> {
  return apiFetch<Crane[]>('/api/cranes/')
}

// Add an MHC.
export function createCrane(payload: CraneInput): Promise<Crane> {
  return apiFetch<Crane>('/api/cranes/', { method: 'POST', body: payload })
}

// Change or retire an MHC.
export function updateCrane(craneId: number, patch: CranePatch): Promise<Crane> {
  return apiFetch<Crane>(`/api/cranes/${craneId}`, { method: 'PATCH', body: patch })
}

// Reference values of one category (nature_of_work, working_area or delay_type), including retired ones.
export function listReferenceData(category: string): Promise<ReferenceData[]> {
  return apiFetch<ReferenceData[]>(`/api/admin/reference-data?category=${encodeURIComponent(category)}`)
}

// Add a reference value.
export function createReferenceData(payload: ReferenceDataInput): Promise<ReferenceData> {
  return apiFetch<ReferenceData>('/api/admin/reference-data', { method: 'POST', body: payload })
}

// Change or retire a reference value.
export function updateReferenceData(id: number, patch: ReferenceDataPatch): Promise<ReferenceData> {
  return apiFetch<ReferenceData>(`/api/admin/reference-data/${id}`, { method: 'PATCH', body: patch })
}