// Route guard: only lets listed roles through; others are sent to /login or to their own home page.
import { Navigate, Outlet } from 'react-router-dom'
import type { Role } from '../api/types'
import { homePathForRole } from './roles'
import { useAuth } from './useAuth'

export default function RequireRole({ allowed }: { allowed: Role[] }) {
  const { user, loading } = useAuth()

  // Wait for the saved session check before deciding anything.
  if (loading) return <p className="status-message">Loading…</p>
  // Not signed in: go to the login page.
  if (!user) return <Navigate to="/login" replace />
  // Signed in but wrong role: go to the page for the user's own role.
  if (!allowed.includes(user.role)) return <Navigate to={homePathForRole(user.role)} replace />
  return <Outlet />
}