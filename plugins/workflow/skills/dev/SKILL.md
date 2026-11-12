---
name: dev
description: Company dev workflow in one flow - clarify the PRD, technical solution doc and test case sheet (or bug diagnosis), branch check and plan, implementation, testing, code review, commits, and pull request. Use when a developer starts a feature, bug, or ticket, provides a PRD or spec, or wants to commit or open a PR. Resumes from whichever stage the work is at.
argument-hint: <PRD path, link, or text | ticket and description | stage name: solution, diagnose, start, build, test, review, commit, pr>
---

# Dev workflow

Input: $ARGUMENTS

Stages run in order: **1 Solution (features) or Diagnose (bugs) → 2 Start → 3 Build → 4 Test → 5 Review → 6 Commit → 7 PR**. After each stage, report briefly and wait for the developer's OK before the next one.

**Checklists** live in this plugin's `references/` folder (two folders up from this skill's directory): `security.md`, `performance.md`, `accessibility.md`, `observability.md`, `migrations.md`, `definition-of-done.md`. The project's quality bar is `docs/quality-bar.md`, if present.

**Project conventions:** the **Workflow** section of `CLAUDE.md` overrides the defaults in this skill (branch naming, protected branches, commit format, PR template, solution docs folder). So does the repo's commitlint config.

**Never:** create, switch, rebase, or merge branches; commit with `--no-verify`; push to a protected branch (default `main`, `master`, `develop`).

## 0. Find where to start

- If the input names a stage (`solution`, `diagnose`, `start`, `build`, `test`, `review`, `commit`, `pr`), go to it.
- If the input is a PRD or spec, start at stage 1 (Solution).
- If the input is a bug report, error, or failing behaviour, start at stage 1 (Diagnose).
- If the input is only a ticket or small task with no PRD, ask whether to write a solution doc or skip to stage 2.
- If there is no input, detect the state and propose where to resume:
  - On a protected branch with no changes: stage 1 or 2.
  - Uncommitted changes and the test sheet has `Not run` or `Retrying` rows: stage 4. Otherwise: stage 5.
  - Commits ahead of the default branch and no PR (`gh pr view` fails): stage 7.
  - A solution doc and test sheet in the solution docs folder that match the branch's ticket or slug: use them for stages 3 and 4.

## 1. Solution (features)

Turn the PRD into a technical solution document. No source code changes in this stage.

**Read the PRD**
- Load it from the given path, link, or pasted text. If none is given, ask for it.
- Give every requirement an ID (`R1`, `R2`, ...). Include acceptance criteria and non-functional asks.

**Clarify.** Run the `workflow:clarify` skill on the PRD. Skip it only if the developer says the PRD is complete. Its confirmed **Decisions** shape the doc; questions for other people go to the doc's **Open questions**. Do not invent product behaviour.

**Analyse the codebase** (read `CLAUDE.md` first, and the module `CLAUDE.md` files of the areas involved). Establish, with file paths as evidence:
- Stack and layering (e.g. route, controller, service, repository, model).
- **Closest existing feature**, traced end to end from entry point to storage and tests. This is the pattern the solution follows.
- API conventions: URL naming, versioning, auth, validation, response and error format, pagination.
- Database conventions: engine, ORM, migration tool and folder, naming, timestamps, soft deletes.
- Reusable helpers, services, components, and types.
- Test conventions.

For broad sweeps use an Explore subagent and keep only its conclusions. Before proposing anything new, confirm it does not already exist.

**Write the document** in the format of `solution-template.md` in this skill's directory. Keep every section and its order; write "None" where a section does not apply.
- Plain, simple English. Short sentences. One idea per bullet. Say each thing once. Readable in about 5 minutes.
- Include every API, database, and code change: less wording, not less detail.
- Each change names the existing file or pattern it follows (`path/to/file.ts:42`).
- Facts about current code come from code you read; anything inferred goes under **Assumptions**.
- Contracts, not implementations: request/response examples, columns, signatures. No full code.
- Every requirement ID appears in section 2 and in at least one test.
- Prefer extending existing code over adding modules; say why when something new is needed.
- Ready to build: no design decision is left to whoever implements it. Every API shape, data type, error-handling strategy, and library choice is decided in the doc or listed as an open question.
- Database, API, and data-format changes follow `migrations.md`: expand, migrate, contract, with deploy order and rollback written in the doc.
- Section 8 (rollout and risks) is checked against `security.md`, `performance.md`, `observability.md`, and, for UI, `accessibility.md`. Name the items that apply; skip the rest.

**Challenge.** Before showing the doc, run the `workflow:challenge` skill on it in document mode (five fresh reviewers: simplicity, comprehension, design risk, codebase fit, implementation readiness). Contract: the PRD requirements, the confirmed Decisions, the quality bar, and `CLAUDE.md` rules. Fix valid findings; put findings that need a decision to the developer.

**Save** to `<solution docs folder>/YYYY-MM-DD-<feature-slug>.md` (default `docs/solutions/`).

**Test case sheet.** Have the independent tester write the cases, so they test what the PRD asks for and not what the doc designs. Start the `workflow:tester` agent in **write-cases** mode with the PRD, the confirmed Decisions from clarify, `CLAUDE.md`, and the sheet path `<same folder>/YYYY-MM-DD-<feature-slug>-test-cases.xlsx`. Do not give it the solution doc. Then check its coverage: every requirement ID has cases. Link the sheet in section 7 of the doc.

**Starting the tester.** Use the Agent tool with `subagent_type: workflow:tester` (never a `fork`; if it is unavailable, a `general-purpose` agent told to follow this plugin's `agents/tester.md`). Its prompt contains only: the mode, the repository path, the absolute paths of its input files, the sheet path, the case IDs (run mode), and the test sheet command `python3 <absolute path of this skill's directory>/testsheet.py`. Never include the conversation, what was built or why, the solution doc, claims that something works, or what you expect the results to be.

Report the doc and sheet paths, a 3-line summary, the number of test cases, and blocking open questions. Wait for approval of both.

## 1. Diagnose (bugs)

Run the `workflow:diagnose` skill, phases 1-4: a command that reproduces the bug, then the confirmed root cause. No permanent code changes yet.

Then have the `workflow:tester` agent write the test sheet `<solution docs folder>/YYYY-MM-DD-<bug-slug>-test-cases.xlsx` in **write-cases** mode, from the bug report and the reproduce command only (see **Starting the tester** in stage 1): the reported bug as a P0 case, plus nearby behaviour that must keep working. A solution doc is needed only if the fix changes APIs, the database, or several modules; then write it as for features.

If the root cause or fix touches shared code, data, or anything hard to undo, run the `workflow:challenge` skill in claim mode on the root cause and proposed fix.

Report the reproduce command, the root cause, the proposed fix, and the sheet path. Wait for approval.

## 2. Start

1. Run `git status --porcelain` and `git branch --show-current`. Mention a dirty tree.
2. **Always ask the developer for the branch name.** Do not propose or invent one. When asking, show the project's naming format from the **Workflow** section of `CLAUDE.md` (default `<type>/<TICKET-ID>-<slug>`) so they can follow it.
3. Ask them to create and switch to that branch themselves, and wait until they confirm. Then check with `git branch --show-current` that it is the current branch and is not protected.
4. If the name does not follow the project's format, say so once; the developer decides.
5. If there is no solution doc, read the code the task touches and give a short plan: files to change, approach, how it will be tested.

## 3. Build

Run the `workflow:build` skill with the solution doc (or the stage 2 plan): thin vertical slices, each tested, working, and **approved by the developer** before the next; a new module starts from a skeleton copied from the closest existing module and ends with its `CLAUDE.md`.

- For a bug, run phases 5-6 of `workflow:diagnose` instead: fix the root cause, add the regression test, remove temporary code.
- Automate the sheet's test cases where the project's test setup allows, and record each in the `automated_test` column (`path/to/test::name`).

## 4. Test

The independent `workflow:tester` agent runs the cases and records the results; you fix. **You never write `status` or `actual` in the sheet yourself**: only the tester marks results, so the code's builder never grades its own work. If there is no sheet (solution stage skipped), first have the tester write one (write-cases mode) from the PRD, ticket, or stage 2 plan.

**Loop:**
1. Start the tester in **run** mode (see **Starting the tester** in stage 1) for every `Not run` or `Retrying` case. It verifies each case (automated test it has read, API call, Playwright in the browser, read-only database query) and records Passed with evidence, Failed with what happened, or Human review needed with what a person should check.
2. Read its report and the sheet (`testsheet.py dump`).
3. For each **Retrying** case (failed attempt 1 or 2): reproduce the failure with a fast command, fix the root cause, not the symptom (stage 3 rules apply), and use `workflow:diagnose` phases 1-4 if the cause is not obvious.
4. Start the tester again for the fixed cases, plus already Passed cases the fix could affect.
5. Repeat until no case is `Not run` or `Retrying`. A case that fails its third attempt becomes **Failed**: stop fixing it and report what was tried on each attempt and your best guess at the cause.

If the developer fixes something and asks for a fresh round, pass `"attempts": 0` for those cases before the next tester run.

If the tester reports an environment problem (app will not start, no seed data) or questions an expected result, bring it to the developer; do not change expected results yourself.

Before finishing, go through `definition-of-done.md` and run the `workflow:quality-bar` skill in `check` mode. Report anything not met.

When done, report the counts (Passed, Failed, Human review needed) with attempts used and list the Failed and Human review cases. Move on only when no P0 case is Failed, or the developer explicitly accepts the failures.

**Red flags**

| If you think... | Then... |
|-----------------|---------|
| "I can see it works, I'll mark it Passed myself" | Only the tester records results. Run the tester. |
| "The unit tests pass, so the case passes" | The tester checks the case's expected result itself, end to end. |
| "It probably works, I'll mark it Passed" | No evidence, no Passed. Run it or mark Human review needed. |
| "This failure is flaky, re-run until green" | Flaky is a bug. Reproduce it and find the cause. |
| "I'll loosen the expected result to match" | The expected result comes from the PRD. Fix the code or raise it as a question. |
| "The quality bar is too strict for this change" | Only the developer can grant an exception, recorded with owner and expiry. |

## 5. Review

Run the `workflow:review` skill (Skill tool) on the branch's changes, including uncommitted work.

- Fix every **Critical** and **Major** finding (stage 3 rules apply). Show the developer the Minor findings and Questions, and fix the ones they choose.
- After fixes, have the `workflow:tester` agent re-run the test cases the fixes could affect (stage 4 loop and attempt limits apply), then review the changed code again.
- Move on when the verdict is `Approve` or `Approve with minor fixes`, or the developer explicitly accepts the remaining findings.

## 6. Commit

1. Review `git status` and `git diff`. Group changes; propose one commit per build slice where slices are independent, and separate commits for unrelated concerns.
2. Run lint and tests from `CLAUDE.md`. If they fail, fix or stop and report.
3. Stage files explicitly by path. No `git add -A` or `git add .`. Never stage secrets, `.env*` files, build output, or large binaries.
4. Default message format:
   ```
   <type>(<scope>): <imperative summary, max 72 chars>

   <why this change was needed>

   Refs: <TICKET-ID>
   ```
   - `type`: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `perf`, `ci`. `scope`: module or area; omit if global.
   - Take `TICKET-ID` from the branch name the developer gave, or ask; omit the footer if there is none.
   - Add `BREAKING CHANGE: <what>` in the footer for breaking changes.
5. Commit, then show `git log -1 --stat`.

## 7. PR

Run the `workflow:pr` skill (add `--draft` if requested). It runs the pre-flight checks, pushes, and opens the PR in the company format.

## Test sheet tool

`testsheet.py` in this skill's directory creates and updates the `.xlsx` sheet. Run it with `python3`; if that fails because `openpyxl` is missing, use `uv run` instead.

```sh
python3 <skill dir>/testsheet.py write <sheet.xlsx> <<'EOF'
[{"id": "TC-001", "requirement": "R1", "title": "...", "steps": ["...", "..."], "expected": "..."}]
EOF
python3 <skill dir>/testsheet.py dump <sheet.xlsx>
```

- Only the `workflow:tester` agent records results (`status`, `actual`). The builder may set `automated_test` and, on the developer's request, `attempts: 0`.
- `write` adds or updates rows by `id` and only changes the fields you pass, so reviewer notes are kept. Recording a result: `{"id": "TC-001", "status": "Passed", "actual": "<evidence>"}`; `last_run` and `attempts` are set automatically, and a third failure turns `Retrying` into `Failed`.
- `dump` prints status counts and every row as JSON.
- Never edit the `.xlsx` any other way. Reviewers edit it in Excel: the Status column is a dropdown and rows are coloured by status.
