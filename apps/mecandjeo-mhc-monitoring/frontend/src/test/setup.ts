// Test setup, loaded before every test file: adds the DOM matchers and resets shared browser state after each test.
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  // Remove anything rendered by the test and forget saved tokens, themes and the applied theme.
  cleanup()
  sessionStorage.clear()
  localStorage.clear()
  document.documentElement.removeAttribute('data-theme')
})