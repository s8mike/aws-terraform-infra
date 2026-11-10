// Tests for the theme picker logic: valid theme ids, applying the theme to the page, and saving it per user.
import { act, renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { DEFAULT_THEME, THEMES, isThemeId } from './themes'
import { useTheme } from './useTheme'

describe('isThemeId', () => {
  it('accepts the four themes and rejects anything else', () => {
    expect(THEMES.map((theme) => theme.id)).toEqual(['soft', 'light', 'grey', 'dark'])
    expect(isThemeId('dark')).toBe(true)
    expect(isThemeId('neon')).toBe(false)
    expect(isThemeId(null)).toBe(false)
  })
})

describe('useTheme', () => {
  it('starts on the default theme and applies it to the page', () => {
    const { result } = renderHook(() => useTheme(7))

    expect(result.current.theme).toBe(DEFAULT_THEME)
    expect(document.documentElement.dataset.theme).toBe('soft')
  })

  it('applies a new theme and saves it for that user', () => {
    const { result } = renderHook(() => useTheme(7))

    act(() => result.current.setTheme('dark'))

    expect(result.current.theme).toBe('dark')
    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(localStorage.getItem('mhc_theme:7')).toBe('dark')
  })

  it('keeps each user\'s choice separate', () => {
    localStorage.setItem('mhc_theme:7', 'dark')

    const first = renderHook(() => useTheme(7))
    const second = renderHook(() => useTheme(8))

    expect(first.result.current.theme).toBe('dark')
    expect(second.result.current.theme).toBe('soft')
  })

  it('ignores an invalid saved value', () => {
    localStorage.setItem('mhc_theme:5', 'neon')

    const { result } = renderHook(() => useTheme(5))

    expect(result.current.theme).toBe('soft')
  })

  it('removes the theme from the page when the signed-in frame goes away', () => {
    const { unmount } = renderHook(() => useTheme(7))
    expect(document.documentElement.dataset.theme).toBe('soft')

    unmount()

    expect(document.documentElement.dataset.theme).toBeUndefined()
  })
})