// Fixed choices for the working-conditions form. The backend stores these as free text (100 characters max).
import type { LookupValue } from '../api/types'

type Option = Pick<LookupValue, 'code' | 'label'>

export const WEATHER_OPTIONS: Option[] = [
  { code: 'clear', label: 'Clear' },
  { code: 'cloudy', label: 'Cloudy' },
  { code: 'rain', label: 'Rain' },
  { code: 'fog', label: 'Fog' },
  { code: 'storm', label: 'Storm' },
]

export const VISIBILITY_OPTIONS: Option[] = [
  { code: 'good', label: 'Good' },
  { code: 'moderate', label: 'Moderate' },
  { code: 'poor', label: 'Poor' },
]

export const WIND_OPTIONS: Option[] = [
  { code: 'calm', label: 'Calm' },
  { code: 'light', label: 'Light' },
  { code: 'moderate', label: 'Moderate' },
  { code: 'strong', label: 'Strong' },
]

export const DECK_OPTIONS: Option[] = [
  { code: 'dry', label: 'Dry' },
  { code: 'wet', label: 'Wet' },
]

export const CONGESTION_OPTIONS: Option[] = [
  { code: 'low', label: 'Low' },
  { code: 'medium', label: 'Medium' },
  { code: 'high', label: 'High' },
]