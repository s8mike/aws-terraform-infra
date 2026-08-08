/**
 * Route protection component.
 *
 * Protects routes using authentication
 * and optional role authorization.
 */

import { Navigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import type { UserRole } from "../types/auth";


interface ProtectedRouteProps {
  children: React.ReactNode;

  // Allowed roles for this route
  allowedRoles?: UserRole[];
}


export default function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {

  const {
    isAuthenticated,
    loading,
    user,
  } = useAuth();


  // Wait for session restoration
  if (loading) {
    return (
      <div>
        Loading...
      </div>
    );
  }


  // Redirect unauthenticated users
  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }


  // Check role authorization when roles are provided
  if (
    allowedRoles &&
    user &&
    !allowedRoles.includes(user.role)
  ) {
    return (
      <Navigate
        to="/access-denied"
        replace
      />
    );
  }


  return children;
}