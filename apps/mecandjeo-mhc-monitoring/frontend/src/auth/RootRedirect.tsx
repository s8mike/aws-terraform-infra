// Handles "/" and unknown URLs: sends signed-in users to their home page and everyone else to /login.
import { Navigate } from 'react-router-dom'
import { homePathForRole } from './roles'
import { useAuth } from './useAuth'

export default function RootRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <p className="status-message">Loading…</p>
  return <Navigate to={user ? homePathForRole(user.role) : '/login'} replace />
}