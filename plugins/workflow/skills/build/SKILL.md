---
name: build
description: Build a feature, new module, or change in thin, working slices - each slice end to end, tested, verified, and approved by the developer before the next, keeping the code working throughout. The standard way to implement any new module or multi-file change. Use when implementing a solution doc, plan, or ticket, creating a new module, or as the build stage of /workflow:dev.
argument-hint: <solution doc, plan, or task>
---

# Build in slices

Work: $ARGUMENTS

Plan source: the solution doc's build order, the plan, or the task. If there is none, write a short plan first (files, approach, tests) and get it approved.

Read `CLAUDE.md`, the module `CLAUDE.md` files of the areas involved, and the project's quality bar (`docs/quality-bar.md`, if present). Do not commit, create branches, or push here: commits happen afterwards, one per slice where that makes sense.

## 1. Slice the work

List the slices before writing code. A slice is the smallest piece that works end to end and can be checked on its own. Choose the order:

- **Vertical (default):** one complete path through the stack per slice. "Create order: migration + API + UI", then "List orders", then "Cancel order".
- **Contract first:** when backend and frontend move in parallel. Slice 0 defines the API contract (types, schema, OpenAPI); then the backend against it, the frontend against mock data that matches it, then integration.
- **Risk first:** when one part is uncertain (a new library, an integration, a performance limit). Prove it in slice 1 before building on it.

Show the slice list with what each one proves, and wait for the developer to approve or change it before writing code.

## 2. New module: skeleton first

When the work creates a new module:
1. Find the closest existing module and copy its structure: folders, layering, naming, how it is registered, wired, and tested.
2. Slice 0 is the skeleton: the module's public interface (types, routes, exported functions) with the simplest possible bodies, registered in the app, with one test that reaches it. The build passes.
3. Fill it in with vertical slices.
4. Last slice: write the module's `CLAUDE.md` (purpose, key files, connections, notes; keep it under about 30 lines) so the next person and Claude can find their way.

## 3. For each slice

1. **Implement** the smallest complete version. Follow the patterns the solution doc cites.
2. **Test** - add or update tests for the slice's behaviour, then run them with the existing tests in the area.
3. **Verify it runs** - the build passes, and the behaviour works when exercised (API call, page, CLI), not only in unit tests.
4. **Record** - which requirement IDs it covers, and any test case IDs it automated (`automated_test` in the test sheet).
5. **Human review** - stop and present the slice for review:
   ```
   Slice <n>/<total>: <name> - covers R1, R3
   Changed: <files, with a one-line note each> (git diff --stat)
   Try it: <exact command, URL, or API call to see it working>
   Tests: <command run> - <result>
   Noticed, not changed: <items, or "none">
   Next: slice <n+1> - <name>
   ```
   Wait for the developer. Do not start the next slice, or any of its code, until they approve.
   - **Approved:** move to the next slice.
   - **Changes requested:** make them inside this slice, re-run its tests, and present it again.
   - **Plan change** (a slice to add, drop, split, or reorder): update the slice list (and the solution doc, if it changes the design) and confirm it before continuing.

Only start the next slice when the current one is green **and** approved by the developer.

## Rules

- **Simplest thing that works.** No abstractions, options, or hooks the task does not need. Three similar lines beat a premature abstraction.
- **Stay in scope.** Do not clean up, refactor, or modernise code the task does not require. List anything worth fixing under **Noticed, not changed** in your report.
- **One concern per slice.** Do not mix a feature, a refactor, and a config change in one slice.
- **Always working.** After every slice the project builds and existing tests pass.
- **Unfinished user-facing features go behind a flag**, using the project's existing feature flag mechanism (or an environment variable if there is none), off by default.
- **Safe defaults.** New options default to the conservative behaviour: off, no notification, no deletion.
- **Easy to undo.** Prefer additive changes. Schema, API, and data-format changes follow `references/migrations.md` (in this plugin, two folders up from this skill).
- **Plan wrong?** Stop, say what you found, and update the solution doc before changing direction.

## Red flags

| If you think... | Then... |
|-----------------|---------|
| "I'll write the tests after all slices" | Each slice is done only when its tests pass. |
| "While I'm here, I'll tidy this file" | Out of scope. Note it under **Noticed, not changed**. |
| "This slice is too small to verify" | Small slices are quick to verify. Verify it. |
| "I'll start the next slice while they review" | Wait for approval. Feedback on this slice can change the next one. |
| "These two slices are small, I'll show them together" | One slice per review. Combined reviews hide problems. |
| "I'll make it generic for later" | Build for the requirements in front of you. |
| "The build is broken but the next slice will fix it" | Fix it now. Every slice ends green. |

## Report

Slices done and approved, requirement IDs covered, tests added, flags introduced, anything left out, and the **Noticed, not changed** list.
