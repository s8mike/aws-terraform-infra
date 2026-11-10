// Helpers for tests that need a signed-in or signed-out auth context: a fake user and a ready-made context value.
import { vi } from 'vitest'
import type { Role, User } from '../api/types'
import type { AuthContextValue } from '../auth/AuthContext'

// A fake user with the given role.
export function makeUser(role: Role): User {
  return {
    id: 1,
    email: `${role}@example.com`,
    full_name: `${role[0].toUpperCase()}${role.slice(1)} User`,
    role,
    is_active: true,
    created_at: '2026-10-07T06:00:00',
    updated_at: '2026-10-07T06:00:00',
  }
}

// An auth context value; signed out and not loading unless overridden.
export function makeAuth(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: null,
    loading: false,
    login: vi.fn<AuthContextValue['login']>(),
    logout: vi.fn<AuthContextValue['logout']>(),
    ...overrides,
  }
}