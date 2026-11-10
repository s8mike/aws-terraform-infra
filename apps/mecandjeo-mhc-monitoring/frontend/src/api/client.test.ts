// Tests for the API client: auth header, request bodies, error messages, the 401 rules, CSV download and time helpers.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  ApiError,
  apiFetch,
  downloadCsv,
  getToken,
  nowUtcIso,
  parseServerDate,
  setToken,
  setUnauthorizedHandler,
} from './client'

const fetchMock = vi.fn()

// A fake server response with an optional JSON body.
function reply(status: number, body?: unknown): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

// Make every fetch call return a fresh fake reply (a Response body can only be read once).
function respondWith(status: number, body?: unknown): void {
  fetchMock.mockImplementation(() => Promise.resolve(reply(status, body)))
}

// The URL and options of the most recent fetch call.
function lastCall(): { url: string; init: RequestInit; headers: Record<string, string> } {
  const [url, init] = fetchMock.mock.calls[fetchMock.mock.calls.length - 1] as [string, RequestInit]
  return { url, init, headers: (init.headers ?? {}) as Record<string, string> }
}

beforeEach(() => {
  fetchMock.mockReset()
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
  setUnauthorizedHandler(null)
})

describe('apiFetch requests', () => {
  it('sends the saved token as a Bearer header', async () => {
    setToken('abc123')
    respondWith(200, { ok: true })

    await apiFetch('/api/lookups')

    expect(lastCall().headers.Authorization).toBe('Bearer abc123')
  })

  it('sends no Authorization header when there is no token or when auth is off', async () => {
    respondWith(200, {})
    await apiFetch('/api/lookups')
    expect(lastCall().headers.Authorization).toBeUndefined()

    setToken('abc123')
    await apiFetch('/api/auth/login', { method: 'POST', body: {}, auth: false })
    expect(lastCall().headers.Authorization).toBeUndefined()
  })

  it('serializes a body as JSON and sets the content type only when there is a body', async () => {
    respondWith(201, {})

    await apiFetch('/api/shifts/start', { method: 'POST', body: { mhc_number: 'MHC-01' } })
    expect(lastCall().init.body).toBe('{"mhc_number":"MHC-01"}')
    expect(lastCall().headers['Content-Type']).toBe('application/json')

    await apiFetch('/api/lookups')
    expect(lastCall().init.body).toBeUndefined()
    expect(lastCall().headers['Content-Type']).toBeUndefined()
  })

  it('returns the parsed JSON, and undefined for a 204', async () => {
    fetchMock.mockResolvedValueOnce(reply(200, { id: 7 }))
    expect(await apiFetch('/api/x')).toEqual({ id: 7 })

    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }))
    expect(await apiFetch('/api/auth/change-password', { method: 'POST', body: {} })).toBeUndefined()
  })
})

describe('apiFetch errors', () => {
  it('throws an ApiError carrying the server message and status', async () => {
    respondWith(409, { detail: 'Operator already has an active shift' })

    const error = await apiFetch('/api/shifts/start', { method: 'POST', body: {} }).catch((caught: unknown) => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(409)
    expect((error as ApiError).message).toBe('Operator already has an active shift')
  })

  it('joins the messages of a validation error list', async () => {
    respondWith(422, { detail: [{ msg: 'Field required' }, { msg: 'Value too short' }] })

    await expect(apiFetch('/api/x')).rejects.toThrow('Field required; Value too short')
  })

  it('falls back to a generic message when the error body is not JSON', async () => {
    fetchMock.mockResolvedValue(new Response('<html>Bad gateway</html>', { status: 502 }))

    await expect(apiFetch('/api/x')).rejects.toBeInstanceOf(ApiError)
  })
})

describe('apiFetch 401 handling', () => {
  it('clears the token and calls the handler for an authenticated 401', async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)
    setToken('expired')
    respondWith(401, { detail: 'Could not validate credentials' })

    await expect(apiFetch('/api/lookups')).rejects.toBeInstanceOf(ApiError)

    expect(getToken()).toBeNull()
    expect(handler).toHaveBeenCalledTimes(1)
  })

  it('does not sign anyone out when a login attempt (auth off) returns 401', async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)
    setToken('still-valid')
    respondWith(401, { detail: 'Invalid email or password' })

    await expect(apiFetch('/api/auth/login', { method: 'POST', body: {}, auth: false })).rejects.toThrow(
      'Invalid email or password',
    )

    expect(getToken()).toBe('still-valid')
    expect(handler).not.toHaveBeenCalled()
  })

  it('keeps the user signed in for a 400 such as a wrong current password', async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)
    setToken('valid')
    respondWith(400, { detail: 'Current password is incorrect' })

    await expect(apiFetch('/api/auth/change-password', { method: 'POST', body: {} })).rejects.toThrow(
      'Current password is incorrect',
    )

    expect(getToken()).toBe('valid')
    expect(handler).not.toHaveBeenCalled()
  })
})

describe('downloadCsv', () => {
  it('sends the auth header and saves the response as a file, then releases the temporary URL', async () => {
    setToken('abc123')
    fetchMock.mockResolvedValue(new Response('a,b\n1,2\n', { status: 200 }))
    const createUrl = vi.fn(() => 'blob:fake')
    const revokeUrl = vi.fn()
    vi.stubGlobal('URL', Object.assign(URL, { createObjectURL: createUrl, revokeObjectURL: revokeUrl }))
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

    await downloadCsv('/api/reports/performance.csv?crane_id=2', 'historical-performance.csv')

    expect(lastCall().headers.Authorization).toBe('Bearer abc123')
    expect(click).toHaveBeenCalledTimes(1)
    expect(createUrl).toHaveBeenCalledTimes(1)
    expect(revokeUrl).toHaveBeenCalledWith('blob:fake')
  })

  it('throws an ApiError when the download is refused', async () => {
    fetchMock.mockResolvedValue(new Response('no', { status: 403 }))

    await expect(downloadCsv('/api/reports/performance.csv', 'x.csv')).rejects.toBeInstanceOf(ApiError)
  })
})

describe('time helpers', () => {
  it('nowUtcIso returns a naive UTC timestamp without a Z', () => {
    const value = nowUtcIso()
    expect(value).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/)
    expect(value.endsWith('Z')).toBe(false)
  })

  it('parseServerDate reads a naive timestamp as UTC and respects an explicit offset', () => {
    expect(parseServerDate('2026-10-07T06:30:00').toISOString()).toBe('2026-10-07T06:30:00.000Z')
    expect(parseServerDate('2026-10-07T06:30:00Z').toISOString()).toBe('2026-10-07T06:30:00.000Z')
    expect(parseServerDate('2026-10-07T07:30:00+01:00').toISOString()).toBe('2026-10-07T06:30:00.000Z')
  })
})