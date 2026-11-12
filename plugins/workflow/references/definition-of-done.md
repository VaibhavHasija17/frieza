# Definition of done

The same bar for every change. Acceptance criteria say "did we build the right thing"; this says "is it finished to our standard". A change is done only when both are met. The project's quality bar (`docs/quality-bar.md`, if it exists) adds measured limits on top.

## Correctness
- Every requirement or acceptance criterion is met and checked by running the code, not only by compiling it.
- New behaviour has tests that fail without the change and pass with it. Existing tests still pass.
- Error paths and edge cases are handled, not only the happy path.

## Quality
- Names say what things do; no comments needed to explain *what* code does.
- No duplicated logic, dead code, debug output, or commented-out code.
- Changes stay inside the task's scope. Things noticed outside it are listed, not fixed.
- Lint, format, and type checks pass.

## Integration
- Works with the rest of the system, not only in isolation.
- Migrations, config, environment variables, and feature flags are in place and documented.
- Changes to anything others depend on follow `migrations.md`.

## Documentation
- Public APIs and user-visible behaviour are documented where the project keeps such docs.
- Module `CLAUDE.md` files are updated if the module's purpose, key files, or connections changed.

## Ready to ship
- Security checked for any input, auth, or data handling (`security.md`).
- New critical paths can be observed in production (`observability.md`).
- Risky changes have a rollback path. One-way doors are called out.
- UI changes meet `accessibility.md`.
- A person has reviewed and approved before merge.
