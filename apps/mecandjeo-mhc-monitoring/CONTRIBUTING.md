# Contributing

This project is being built phase by phase.

## Working Rules

- Complete one phase before starting the next.
- Document every completed phase.
- Run available checks before moving on.
- Keep security decisions explicit.
- Add inline comments where they help beginners understand the code.
- Keep real secrets out of Git.

## Documentation Rule

Each phase should update:

- `Roadmap.md`
- `docs/PROJECT-PHASES.md`
- Any topic-specific doc affected by the phase
- `PROJECT-STATUS.md`
- `CHANGELOG.md` when behavior or structure changes

## Testing Rule

Each phase should include the best available verification:

- Syntax checks for code-only phases.
- Unit tests where business logic exists.
- API tests when routes are implemented.
- Docker checks when local runtime is ready.
- Terraform validation when infrastructure is implemented.

## Phase Completion Rule

After each phase:

- Run the available verification commands.
- Update the phase documentation.
- Summarize known gaps.
- Ask before pushing to the upstream Git remote.
