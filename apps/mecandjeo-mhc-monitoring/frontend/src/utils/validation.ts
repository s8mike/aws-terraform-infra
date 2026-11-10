// Client-side checks that mirror the backend rules, so people get instant feedback before the server is called.

// One password rule: a short label for the live checklist, the message shown on submit, and whether it is met.
export interface PasswordCheck {
  label: string
  message: string
  met: boolean
}

// The backend policy: 8-128 characters with a lowercase letter, an uppercase letter, a digit and one of ! @ # % $.
export function passwordChecks(password: string): PasswordCheck[] {
  return [
    { label: 'At least 8 characters', message: 'Password must be at least 8 characters.', met: password.length >= 8 },
    { label: 'A lowercase letter', message: 'Password must include a lowercase letter.', met: /[a-z]/.test(password) },
    { label: 'An uppercase letter', message: 'Password must include an uppercase letter.', met: /[A-Z]/.test(password) },
    { label: 'A number', message: 'Password must include a number.', met: /[0-9]/.test(password) },
    { label: 'One of ! @ # % $', message: 'Password must include one of ! @ # % $', met: /[!@#%$]/.test(password) },
  ]
}

// The first problem with a password, or null when it is acceptable.
export function passwordProblem(password: string): string | null {
  if (password.length > 128) return 'Password must be at most 128 characters.'
  const failed = passwordChecks(password).find((check) => !check.met)
  return failed ? failed.message : null
}