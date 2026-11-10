// Tests for the password rules that mirror the backend policy (checklist items and the first-problem message).
import { describe, expect, it } from 'vitest'
import { passwordChecks, passwordProblem } from './validation'

// Labels of the rules that a password meets, in checklist order.
function metLabels(password: string): string[] {
  return passwordChecks(password)
    .filter((check) => check.met)
    .map((check) => check.label)
}

describe('passwordChecks', () => {
  it('lists five rules, none met for an empty password', () => {
    const checks = passwordChecks('')
    expect(checks).toHaveLength(5)
    expect(checks.every((check) => !check.met)).toBe(true)
  })

  it('evaluates each rule independently', () => {
    expect(metLabels('abc')).toEqual(['A lowercase letter'])
    expect(metLabels('ABC')).toEqual(['An uppercase letter'])
    expect(metLabels('123')).toEqual(['A number'])
    expect(metLabels('!@#')).toEqual(['One of ! @ # % $'])
    expect(metLabels('abcdefgh')).toEqual(['At least 8 characters', 'A lowercase letter'])
  })

  it('meets every rule for the demo password', () => {
    expect(passwordChecks('Securepass123!').every((check) => check.met)).toBe(true)
  })
})

describe('passwordProblem', () => {
  it('accepts a valid password', () => {
    expect(passwordProblem('Brandnew456#')).toBeNull()
  })

  it.each([
    ['Ab1!', 'Password must be at least 8 characters.'],
    ['ALLUPPERCASE1!', 'Password must include a lowercase letter.'],
    ['alllowercase1!', 'Password must include an uppercase letter.'],
    ['NoDigitsHere!', 'Password must include a number.'],
    ['NoSpecial123', 'Password must include one of ! @ # % $'],
  ])('explains why "%s" is rejected', (password, message) => {
    expect(passwordProblem(password)).toBe(message)
  })

  it('does not accept special characters outside the allowed set', () => {
    expect(passwordProblem('Abcdefg1&')).toBe('Password must include one of ! @ # % $')
  })

  it('rejects passwords longer than 128 characters', () => {
    expect(passwordProblem(`Aa1!${'x'.repeat(125)}`)).toBe('Password must be at most 128 characters.')
  })
})