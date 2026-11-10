// Holds the sign-in state for the whole app: restores a saved session on load and handles expiry.
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fetchCurrentUser, requestLogin } from '../api/auth'
import { clearToken, getToken, setToken, setUnauthorizedHandler } from '../api/client'
import type { User } from '../api/types'
import { AuthContext, type AuthContextValue } from './AuthContext'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  // Only start in the loading state when a saved token exists and must be checked with the server.
  const [loading, setLoading] = useState<boolean>(() => getToken() !== null)

  // Any 401 from the API (for example an expired token) clears the user; route guards then show /login.
  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null))
    return () => setUnauthorizedHandler(null)
  }, [])

  // On first load, restore the session from the saved token.
  useEffect(() => {
    if (getToken() === null) return undefined
    let cancelled = false
    fetchCurrentUser()
      .then((me) => {
        if (!cancelled) setUser(me)
      })
      .catch(() => {
        clearToken()
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  // Log in, save the token, then load the user so the caller knows the role.
  const login = useCallback(async (email: string, password: string): Promise<User> => {
    const token = await requestLogin({ email, password })
    setToken(token.access_token)
    try {
      const me = await fetchCurrentUser()
      setUser(me)
      return me
    } catch (error) {
      clearToken()
      throw error
    }
  }, [])

  // Forget the token and the user; route guards redirect to /login.
  const logout = useCallback(() => {
    clearToken()
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, login, logout }),
    [user, loading, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}