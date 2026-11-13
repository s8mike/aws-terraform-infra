# Questions And Improvement Updates

This document tracks suggestions from `docs/Questions-Improvements.md` and records whether each item has been implemented, deferred, or planned for a later phase.

## Current Review

| Suggestion | Status | Notes |
| --- | --- | --- |
| Include the purpose of each test | Implemented | Phase 4, 5, 6, and 7 tests include purpose comments. Documentation explains what the test suite verifies. |
| Include Git Bash commands alongside PowerShell | Implemented | `docs/1. LOCAL-DEVELOPMENT.md` now includes both command styles. |
| Require stronger passwords | Implemented | Registration now requires lowercase, uppercase, number, and one of `!`, `@`, `#`, `%`, `$`. |
| Email should follow a normal email format such as `john-Doe@example.com` | Implemented | `EmailStr` validates email format. Tests include `john-Doe@example.com`. Emails are normalized to lowercase before storage for consistent login behavior. |
| Push every phase upstream on completion | Planned process | This is documented in `CONTRIBUTING.md`. I will not push without explicit confirmation after each phase verification. |
| Each file should have an intro inline comment | In progress | New Phase 4 through 8 files include intro comments. Existing files continue to receive them when touched. |
| `ended_at` should not be empty when a shift or record ends | Implemented | Start payloads can leave `ended_at` empty while active. End payloads require `ended_at`. Endpoints reject invalid close times. |
| Operator should select Shift A, B, or C | Implemented | Shift start validates `shift_code` as `A`, `B`, or `C`. |
| Add the phase where code is introduced | Implemented going forward | New Phase 4 comments identify Phase 4 additions. |
| Separate `loading_export_3_4` into free-bay and across-heights work | Implemented | Phase 6 seed values now use `loading_export_free_bay` and `loading_export_across_heights`. |
| Give known delay types concise keys | Implemented | Phase 6 managed delay reference data includes keys such as `AConE`, `AConX`, `AT`, `AClerks`, `AStev`, and `CT`. Values can be edited by admins. |
| Manage work types, working areas, delays, and shift labels centrally | Implemented | Phase 6 adds the `reference_data` table, admin endpoints, and an idempotent default seed helper. |
| Repeat each phase's individual tests after all phases are complete | Planned process | A final verification matrix will run the focused test file for each phase, then the full suite, before presentation readiness. Each test keeps a purpose comment. |
| Align the Roadmap application structure with current files | Implemented | Phase 8 replaces the stale planned tree with the current routes, services, documentation, and test files. |
| Define what follows Phase 10, including frontend and DevOps learning | Implemented as roadmap | `Roadmap.md` now defines frontend, CI/CD, Kubernetes, Helm, Argo CD GitOps, observability, and presentation-readiness phases. |
| Validate the FastAPI application with PostgreSQL through Docker Compose | Implemented | Phase 8 verified healthy app and database services, `/health`, and all 13 application tables. |

## Still Planned Ahead

- GitHub push after phase completion, after explicit user approval.
- Production-grade rate limiting and account lockout.
- First production-admin bootstrap process (needed before a production environment can use the admin workflow).
- Enforcing active reference-data choices on operator requests; current routes preserve existing string-input compatibility until form/API migration work is scheduled.
