// Defines the shared sign-in state (current user, loading flag, login and logout actions).
import { createContext } from 'react'
import type { User } from '../api/types'

export interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<User>
  logout: () => void
}

// null means "no provider above this component"; useAuth() turns that into a clear error.
export const AuthContext = createContext<AuthContextValue | null>(null)