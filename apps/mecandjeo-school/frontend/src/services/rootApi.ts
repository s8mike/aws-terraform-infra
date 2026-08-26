/**
 * Root-level Axios API client.
 *
 * Used for backend routes that are mounted
 * outside the /api namespace.
 *
 * Examples:
 *   /admin
 *   /students
 *   /teachers
 *   /courses
 *
 * Phase 17.15.2 - API Route Architecture
 */

import axios from "axios";

// The API origin is derived from the configured
// frontend API base URL while removing a trailing
// /api namespace when one is present.
const API_ORIGIN =
  import.meta.env.VITE_API_BASE_URL.replace(/\/api\/?$/, "");

// Create an Axios client for root-level API routes.
const rootApi = axios.create({
  baseURL: API_ORIGIN,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach the existing JWT to root-level API requests.
rootApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default rootApi;