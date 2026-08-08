/**
 * Global authentication context.
 * Manages user session and authentication state.
 */

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import type {
  AuthState,
  LoginResponse,
  User,
} from "../types/auth";

// Authentication context contract
interface AuthContextType extends AuthState {
  login: (data: LoginResponse) => void;
  logout: () => void;
}

// Context instance
const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

// Local storage keys
// Centralized to avoid repeating magic strings.
const USER_STORAGE_KEY = "user";
const TOKEN_STORAGE_KEY = "token";

// Authentication provider
export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  // Current authenticated user
  const [user, setUser] = useState<User | null>(null);

  // Current JWT token
  const [token, setToken] = useState<string | null>(null);

  // Session restoration status
  const [loading, setLoading] = useState(true);

  // Restore session from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem(
      USER_STORAGE_KEY
    );

    const storedToken = localStorage.getItem(
      TOKEN_STORAGE_KEY
    );

    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
      setToken(storedToken);
    }

    setLoading(false);
  }, []);

  // Save authentication data after login
  const login = (data: LoginResponse) => {
    setUser(data.user);
    setToken(data.access_token);

    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify(data.user)
    );

    localStorage.setItem(
      TOKEN_STORAGE_KEY,
      data.access_token
    );
  };

  // Clear authentication data during logout
  const logout = () => {
    setUser(null);
    setToken(null);

    localStorage.removeItem(USER_STORAGE_KEY);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!token,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook for accessing authentication state
export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used within AuthProvider"
    );
  }

  return context;
}