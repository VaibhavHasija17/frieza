---
name: start
description: Start work on a ticket or task - check the working tree, suggest a correctly named branch, and plan before editing. Use when beginning a new feature, bug fix, or ticket.
argument-hint: <ticket-id> <short description>
---

# Start work

Input: $ARGUMENTS

Do not create, switch, or rebase branches. The developer manages branches.

The **Workflow** section of CLAUDE.md overrides the defaults below (branch naming, protected branches).

1. Run `git status --porcelain` and `git branch --show-current`. If the tree is dirty, mention it.
2. Suggest a branch name, as text only. Default format: `<type>/<TICKET-ID>-<slug>`
   - `type`: one of `feat`, `fix`, `chore`, `refactor`, `docs`, `test`. Infer it from the description.
   - `TICKET-ID`: as given (e.g. `ABC-123`). Omit the segment if there is no ticket.
   - `slug`: 3-5 lowercase words, hyphen-separated.
   If the current branch is protected (default: `main`, `master`, `develop`), remind the developer to create a feature branch before committing.
3. Read the code the task touches. Before editing, reply with a short plan: files to change, approach, how it will be tested. Wait for approval if the change spans more than a few files.
