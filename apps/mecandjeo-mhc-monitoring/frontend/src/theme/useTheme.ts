// Hook that loads the signed-in user's saved theme, applies it to the page, and saves changes in this browser.
import { useCallback, useLayoutEffect, useState } from 'react'
import { DEFAULT_THEME, isThemeId, type ThemeId } from './themes'

// One storage entry per user, so two people sharing a computer keep their own choice.
function storageKey(userId: number | undefined): string {
  return `mhc_theme:${userId ?? 'anonymous'}`
}

// Read the saved theme; fall back to the default if nothing valid is saved or storage is unavailable.
function readSavedTheme(userId: number | undefined): ThemeId {
  try {
    const saved = window.localStorage.getItem(storageKey(userId))
    return isThemeId(saved) ? saved : DEFAULT_THEME
  } catch {
    return DEFAULT_THEME
  }
}

export function useTheme(userId: number | undefined) {
  const [theme, setThemeState] = useState<ThemeId>(() => readSavedTheme(userId))

  // Apply the theme to <html> before the screen paints; remove it when the signed-in frame goes away (sign out).
  useLayoutEffect(() => {
    document.documentElement.dataset.theme = theme
    return () => {
      delete document.documentElement.dataset.theme
    }
  }, [theme])

  // Change the theme and remember it for this user.
  const setTheme = useCallback(
    (next: ThemeId) => {
      setThemeState(next)
      try {
        window.localStorage.setItem(storageKey(userId), next)
      } catch {
        // Storage can be blocked by browser settings; the choice then lasts until the page is reloaded.
      }
    },
    [userId],
  )

  return { theme, setTheme }
}