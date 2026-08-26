/**
 * Administrator dashboard service.
 *
 * Handles API communication for administrator
 * dashboard statistics.
 *
 * Phase 17.15.3 - Live Admin Dashboard Integration
 */

import rootApi from "./rootApi";

/**
 * Represents the summary statistics returned
 * by the backend administrator dashboard.
 */
export interface AdminDashboardResponse {
  total_users: number;
  total_students: number;
  total_teachers: number;
  total_courses: number;
  total_assignments: number;
}

/**
 * Retrieve administrator dashboard statistics.
 *
 * The root-level Axios client automatically
 * attaches the JWT Authorization header.
 */
export async function getAdminDashboard(): Promise<AdminDashboardResponse> {
  const response =
    await rootApi.get<AdminDashboardResponse>(
      "/admin/dashboard"
    );

  return response.data;
}