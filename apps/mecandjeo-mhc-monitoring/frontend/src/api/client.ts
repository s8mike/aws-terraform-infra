// Single place that talks to the backend: attaches the token, parses errors, handles 401.
const TOKEN_KEY = 'mhc_token'

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY)
}

// The app registers a handler (for example "go to the login page") that runs on any 401.
let onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  onUnauthorized = handler
}

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// FastAPI sends {"detail": "text"} for most errors and {"detail": [{"msg": ...}]} for validation errors.
function messageFromDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) =>
        typeof item === 'object' && item !== null && 'msg' in item
          ? String((item as { msg: unknown }).msg)
          : String(item),
      )
      .join('; ')
  }
  return 'Request failed'
}

interface RequestOptions {
  method?: string
  body?: unknown
  auth?: boolean
}

// Paths must match the backend exactly, including trailing slashes (for example "/api/cranes/").
export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true } = options
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  // A 401 on an authenticated call means the token is missing or expired.
  // Login itself uses auth: false, so a wrong password does not trigger a redirect.
  if (response.status === 401 && auth) {
    clearToken()
    onUnauthorized?.()
  }

  if (!response.ok) {
    let message = response.statusText || 'Request failed'
    try {
      const data = await response.json()
      message = messageFromDetail(data.detail)
    } catch {
      // The body was not JSON; keep the default message.
    }
    throw new ApiError(response.status, message)
  }

  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

// CSV endpoints need the auth header, so a plain link will not work: fetch a blob and save it.
export async function downloadCsv(path: string, filename: string): Promise<void> {
  const token = getToken()
  const response = await fetch(path, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (response.status === 401) {
    clearToken()
    onUnauthorized?.()
  }
  if (!response.ok) throw new ApiError(response.status, 'Download failed')

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

// Send timestamps as naive UTC (no "Z"), the format the backend stores and compares.
export function nowUtcIso(): string {
  return new Date().toISOString().slice(0, 19)
}

// Server timestamps are naive UTC; add "Z" so the browser shows them in local time.
export function parseServerDate(value: string): Date {
  return new Date(/Z$|[+-]\d{2}:\d{2}$/.test(value) ? value : `${value}Z`)
}