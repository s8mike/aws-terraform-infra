// Hook that gives any component access to the signed-in user and the login/logout actions.
import { useContext } from 'react'
import { AuthContext, type AuthContextValue } from './AuthContext'

// Read the auth state; fails loudly if used outside <AuthProvider>.
export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext)
  if (value === null) {
    throw new Error('useAuth must be used inside <AuthProvider>')
  }
  return value
}