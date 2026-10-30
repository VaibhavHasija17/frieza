---
name: commit
description: Create a commit following company conventions (Conventional Commits, ticket reference, checks run first). Use whenever committing changes.
argument-hint: [optional hint about the change]
---

# Commit

Hint: $ARGUMENTS

The **Workflow** section of CLAUDE.md overrides the default commit format below. So does the repo's commitlint config.

1. Review `git status` and `git diff` (staged and unstaged). Group the changes; if they cover unrelated concerns, propose separate commits.
2. Run the project's lint and test commands listed in CLAUDE.md. If they fail, fix or stop and report. Never commit with `--no-verify`.
3. Stage files explicitly by path. Do not use `git add -A` or `git add .`. Never stage secrets, `.env*` files, build output, or large binaries.
4. Write the message. Default format:
   ```
   <type>(<scope>): <imperative summary, max 72 chars>

   <why this change was needed; what was wrong or missing>

   Refs: <TICKET-ID>
   ```
   - `type`: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `perf`, `ci`.
   - `scope`: the module or area touched; omit if global.
   - Take `TICKET-ID` from the branch name (`feat/ABC-123-...`). Omit the footer if there is none.
   - Add `BREAKING CHANGE: <what>` in the footer for breaking changes.
5. Commit, then show `git log -1 --stat`.
