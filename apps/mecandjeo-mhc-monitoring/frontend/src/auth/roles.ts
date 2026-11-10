// Maps each role to the page it lands on after login and when it opens a page it may not use.
import type { Role } from '../api/types'

const HOME_PATHS: Record<Role, string> = {
  operator: '/operator',
  manager: '/manager',
  admin: '/admin',
}

// Return the home path for a role.
export function homePathForRole(role: Role): string {
  return HOME_PATHS[role]
}