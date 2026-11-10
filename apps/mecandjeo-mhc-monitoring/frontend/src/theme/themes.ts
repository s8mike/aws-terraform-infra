// The color themes a signed-in user can pick from the header dropdown. "soft" is the default look.
export type ThemeId = 'soft' | 'light' | 'grey' | 'dark'

export const THEMES: { id: ThemeId; label: string }[] = [
  { id: 'soft', label: 'Soft color' },
  { id: 'light', label: 'Light' },
  { id: 'grey', label: 'Grey' },
  { id: 'dark', label: 'Dark' },
]

export const DEFAULT_THEME: ThemeId = 'soft'

// True when a stored or selected value is one of the known themes.
export function isThemeId(value: unknown): value is ThemeId {
  return THEMES.some((theme) => theme.id === value)
}