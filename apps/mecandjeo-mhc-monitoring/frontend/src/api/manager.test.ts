// Tests for the manager API helpers: query strings leave out empty filters, and each call hits the exact backend path.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { buildQuery, fetchPerformanceTrends, reportCsvPath } from './manager'

const fetchMock = vi.fn()

beforeEach(() => {
  fetchMock.mockReset()
  fetchMock.mockResolvedValue(new Response('[]', { status: 200 }))
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('buildQuery', () => {
  it('returns an empty string when there are no filters', () => {
    expect(buildQuery({})).toBe('')
    expect(buildQuery({ date_from: undefined, nature_of_work: '' })).toBe('')
  })

  it('keeps only the filters that have a value, including numbers', () => {
    expect(buildQuery({ crane_id: 2, nature_of_work: 'loading', date_from: undefined })).toBe(
      '?crane_id=2&nature_of_work=loading',
    )
  })

  it('encodes values safely', () => {
    expect(buildQuery({ date_from: '2026-10-08T00:00:00' })).toBe('?date_from=2026-10-08T00%3A00%3A00')
  })
})

describe('manager calls', () => {
  it('reportCsvPath points at the CSV route with the same filters', () => {
    expect(reportCsvPath({ crane_id: 3 })).toBe('/api/reports/performance.csv?crane_id=3')
    expect(reportCsvPath({})).toBe('/api/reports/performance.csv')
  })

  it('fetchPerformanceTrends sends group_by and the date range to the trends route', async () => {
    await fetchPerformanceTrends('nature_of_work', { date_from: '2026-10-01T00:00:00' })

    const [url] = fetchMock.mock.calls[0] as [string]
    expect(url.startsWith('/api/manager/performance/trends?')).toBe(true)
    expect(url).toContain('group_by=nature_of_work')
    expect(url).toContain('date_from=2026-10-01T00%3A00%3A00')
  })
})