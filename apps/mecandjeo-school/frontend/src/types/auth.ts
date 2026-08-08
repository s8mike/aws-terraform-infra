/**
 * Authentication models shared across the application.
 * These interface Defines the contract between 
 * the React frontend and FastAPI backend for authentication data.
 * 
 * Phase 13.2 - Step 4C
 */

// Login request payload
export interface LoginRequest {
  email: string;
  password: string;
}

// Supported user roles
export type UserRole =
  | "admin"
  | "teacher"
  | "student"
  | "parent";

// Authenticated user returned by the backend
export interface User {
  id: number;
  email: string;
  role: UserRole;
}

// Login response returned after authentication
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Global authentication state
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}