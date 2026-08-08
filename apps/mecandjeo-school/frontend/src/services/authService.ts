/**
 * Authentication service.
 *
 * Handles authentication-related
 * API communication.
 */

import api from "./api";

import type {
  LoginRequest,
  LoginResponse,
} from "../types/auth";


// Login user
export async function login(
  credentials: LoginRequest
): Promise<LoginResponse> {

  const response = await api.post<LoginResponse>(
    "/login",
    credentials
  );

  return response.data;
}