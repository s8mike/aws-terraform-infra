// Turns any caught error into a short message that is safe to show on screen.
import { ApiError } from '../api/client'

// Server errors keep the server's message; anything else usually means the API is unreachable.
export function errorMessage(caught: unknown): string {
  return caught instanceof ApiError ? caught.message : 'Could not reach the server. Is the API running?'
}