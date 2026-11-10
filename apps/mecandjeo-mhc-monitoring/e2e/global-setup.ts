// Runs once before all tests: stops early with a clear message when the stack is not running or the admin password is unknown.
import type { FullConfig } from '@playwright/test'
import { adminPassword } from './helpers/env'

export default async function globalSetup(config: FullConfig): Promise<void> {
  const baseURL = config.projects[0].use.baseURL ?? 'http://localhost:8080'

  let healthy = false
  try {
    healthy = (await fetch(`${baseURL}/health`)).ok
  } catch {
    healthy = false
  }
  if (!healthy) {
    throw new Error(
      `The stack is not answering at ${baseURL}/health.\n` +
        'Start it from apps/mecandjeo-mhc-monitoring with: docker compose --env-file .env.docker up -d',
    )
  }

  if (!adminPassword) {
    throw new Error('The admin password was not found. Set BOOTSTRAP_ADMIN_PASSWORD in .env.docker or E2E_ADMIN_PASSWORD.')
  }
}