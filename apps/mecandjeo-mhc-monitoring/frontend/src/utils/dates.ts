// Date helpers for filter forms: people pick local calendar days, the API compares naive UTC timestamps.

// Start of a local day ("2026-10-08") as a naive UTC timestamp, or undefined when no day is chosen.
export function startOfLocalDayUtc(day: string): string | undefined {
  if (!day) return undefined
  return new Date(`${day}T00:00:00`).toISOString().slice(0, 19)
}

// End of a local day as a naive UTC timestamp, or undefined when no day is chosen.
export function endOfLocalDayUtc(day: string): string | undefined {
  if (!day) return undefined
  return new Date(`${day}T23:59:59`).toISOString().slice(0, 19)
}