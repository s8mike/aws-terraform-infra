// Auth API calls: login, public operator registration, "who am I", and changing your own password.
import { apiFetch } from './client'
import type { LoginRequest, RegisterRequest, Token, User } from './types'

// What the change-password endpoint expects.
export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

// Exchange email and password for a token. auth:false so a wrong password never triggers the 401 redirect.
export function requestLogin(credentials: LoginRequest): Promise<Token> {
  return apiFetch<Token>('/api/auth/login', { method: 'POST', body: credentials, auth: false })
}

// Public registration; the backend only allows the operator role here.
export function registerOperator(payload: RegisterRequest): Promise<User> {
  return apiFetch<User>('/api/auth/register', { method: 'POST', body: payload, auth: false })
}

// Read the signed-in user from the saved token (used to restore a session after a page reload).
export function fetchCurrentUser(): Promise<User> {
  return apiFetch<User>('/api/auth/me')
}

// Change the signed-in user's own password. A wrong current password returns 400, so the user stays signed in.
export function changePassword(payload: ChangePasswordRequest): Promise<void> {
  return apiFetch<void>('/api/auth/change-password', { method: 'POST', body: payload })
}