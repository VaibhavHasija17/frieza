---
name: dev
description: Company dev workflow in one flow - PRD to technical solution doc and test case sheet, branch check and plan, implementation, testing, code review, commits, and pull request. Use when a developer starts a feature or ticket, provides a PRD or spec, or wants to commit or open a PR. Resumes from whichever stage the work is at.
argument-hint: <PRD path, link, or text | ticket and description | stage name: solution, start, build, test, review, commit, pr>
---

# Dev workflow

Input: $ARGUMENTS

Stages run in order: **1 Solution → 2 Start → 3 Build → 4 Test → 5 Review → 6 Commit → 7 PR**. After each stage, report briefly and wait for the developer's OK before the next one.

**Project conventions:** the **Workflow** section of `CLAUDE.md` overrides the defaults in this skill (branch naming, protected branches, commit format, PR template, solution docs folder). So does the repo's commitlint config.

**Never:** create, switch, rebase, or merge branches; commit with `--no-verify`; push to a protected branch (default `main`, `master`, `develop`).

## 0. Find where to start

- If the input names a stage (`solution`, `start`, `build`, `test`, `review`, `commit`, `pr`), go to it.
- If the input is a PRD or spec, start at stage 1.
- If the input is only a ticket or small task with no PRD, ask whether to write a solution doc or skip to stage 2.
- If there is no input, detect the state and propose where to resume:
  - On a protected branch with no changes: stage 1 or 2.
  - Uncommitted changes and the test sheet has `Not run` or `Retrying` rows: stage 4. Otherwise: stage 5.
  - Commits ahead of the default branch and no PR (`gh pr view` fails): stage 7.
  - A solution doc and test sheet in the solution docs folder that match the branch's ticket or slug: use them for stages 3 and 4.

## 1. Solution

Turn the PRD into a technical solution document. No source code changes in this stage.

**Read the PRD**
- Load it from the given path, link, or pasted text. If none is given, ask for it.
- Give every requirement an ID (`R1`, `R2`, ...). Include acceptance criteria and non-functional asks.
- Anything ambiguous goes to **Open questions**. Do not invent product behaviour.

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

**Save** to `<solution docs folder>/YYYY-MM-DD-<feature-slug>.md` (default `docs/solutions/`).

**Test case sheet.** Generate test cases from the PRD into `<same folder>/YYYY-MM-DD-<feature-slug>-test-cases.xlsx`, using `testsheet.py` (see "Test sheet tool" below).
- Every requirement ID gets at least one positive case, plus negative, edge, permission, and validation cases where they apply.
- Each case: `id` (`TC-001`...), `requirement`, `title`, `type` (Functional, Negative, Edge, UI, API, DB, Security, Performance), `priority` (P0 blocks release, P1, P2), `preconditions`, `steps` (list), `test_data`, `expected`.
- Expected results must be observable and specific (status code, message, row in a table, element on screen), not "works correctly".
- Cases come from the PRD's behaviour, not from the planned code. Link the sheet in section 7 of the doc.

Report the doc and sheet paths, a 3-line summary, the number of test cases, and blocking open questions. Wait for approval of both.

## 2. Start

1. Run `git status --porcelain` and `git branch --show-current`. Mention a dirty tree.
2. Suggest a branch name as text only. Default format `<type>/<TICKET-ID>-<slug>`:
   - `type`: `feat`, `fix`, `chore`, `refactor`, `docs`, or `test`.
   - `TICKET-ID` as given (e.g. `ABC-123`); omit the segment if there is no ticket.
   - `slug`: 3-5 lowercase words, hyphen-separated.
3. If the current branch is protected, ask the developer to create the branch, and wait until they confirm.
4. If there is no solution doc, read the code the task touches and give a short plan: files to change, approach, how it will be tested.

## 3. Build

- Follow the solution doc's build order (or the stage 2 plan), one task at a time.
- Follow the patterns the doc cites. Stay within its scope. If the plan turns out wrong, say so and update the doc before changing direction.
- After each task, run the relevant lint and tests from `CLAUDE.md`, and fix failures before moving on.
- Add or update automated tests for the sheet's test cases where the project's test setup allows. Record each in the sheet's `automated_test` column (`path/to/test::name`).
- When done, list what was built against the requirement IDs and anything left out.

## 4. Test

Run every test case in the sheet and record the result. If there is no sheet (solution stage skipped), first generate one from the PRD, ticket, or stage 2 plan as in stage 1.

**How to verify each case,** most reliable first:
1. Automated test: run it (single-test command from `CLAUDE.md`) and use its result.
2. API: call the endpoint on the local dev server (`curl`) and compare status and body with the expected result.
3. UI: use the Playwright MCP tools against the local dev server: follow the steps, check the expected element or text, take a screenshot for evidence.
4. DB: query the local database to confirm the expected rows or values.

**Status rules:**
- **Passed** - you ran it and the actual result matches the expected result. Evidence is required: the test name and command, the response, or the screenshot path. No evidence, no Passed.
- **Failed** - the actual result differs. Record it as `"status": "Failed"` with what happened. Each case gets **3 attempts**; the tool counts them:
  - Attempts 1 and 2: the tool marks the case **Retrying**. Find the root cause, fix it (stage 3 rules apply), and re-run the case.
  - Attempt 3: the tool marks it **Failed**. Stop fixing that case. Report what was tried on each attempt and your best guess at the cause.
  - After a fix, re-run the already Passed cases the fix could affect.
  - If the developer fixes something and asks for a fresh round, pass `"attempts": 0` with the next result.
- **Human review needed** - you cannot verify it reliably yourself. Say exactly what the person should check. Use this for: visual design and UX judgement, wording and copy, third-party systems (payments, email, SMS, external APIs), real devices or browsers you cannot run, production-like data or credentials you do not have, requirements with open questions, and anything only partly verified.

Never test against production or shared environments, and never use real customer data. Record results in the sheet as you go, not at the end. Stage 4 ends only when no case is `Not run` or `Retrying`.

When done, report the counts (Passed, Failed, Human review needed) with attempts used and list the Failed and Human review cases. Move on only when no P0 case is Failed, or the developer explicitly accepts the failures.

## 5. Review

Run the `workflow:review` skill (Skill tool) on the branch's changes, including uncommitted work.

- Fix every **Critical** and **Major** finding (stage 3 rules apply). Show the developer the Minor findings and Questions, and fix the ones they choose.
- After fixes, re-run the test cases the fixes could affect (stage 4 rules and attempt limits apply), then review the changed code again.
- Move on when the verdict is `Approve` or `Approve with minor fixes`, or the developer explicitly accepts the remaining findings.

## 6. Commit

1. Review `git status` and `git diff`. Group changes; propose separate commits for unrelated concerns.
2. Run lint and tests from `CLAUDE.md`. If they fail, fix or stop and report.
3. Stage files explicitly by path. No `git add -A` or `git add .`. Never stage secrets, `.env*` files, build output, or large binaries.
4. Default message format:
   ```
   <type>(<scope>): <imperative summary, max 72 chars>

   <why this change was needed>

   Refs: <TICKET-ID>
   ```
   - `type`: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `perf`, `ci`. `scope`: module or area; omit if global.
   - Take `TICKET-ID` from the branch name; omit the footer if there is none.
   - Add `BREAKING CHANGE: <what>` in the footer for breaking changes.
5. Commit, then show `git log -1 --stat`.

## 7. PR

1. Confirm the branch is not protected and the tree is clean (otherwise go back to stage 6).
2. Find the default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`). Run `git fetch origin` and `git rev-list --count HEAD..origin/<default>`. If behind, tell the developer by how many commits. Do not rebase or merge.
3. Run lint and tests. Do not open the PR if they fail. Read the test sheet with `testsheet.py dump`, including statuses and notes reviewers changed in Excel. Do not open the PR with `Not run` or `Retrying` cases, or Failed P0 cases, unless the developer accepts them.
4. If code changed since the stage 5 review (or stage 5 was skipped), run the `workflow:review` skill again on the branch. Do not open the PR with open Critical or Major findings unless the developer accepts them.
5. `git push -u origin HEAD`.
6. `gh pr create` (add `--draft` if requested):
   - Title: same format as the main commit.
   - Body: the repo's PR template if it has one. Otherwise:
     ```
     ## Summary
     <what and why, 1-3 sentences>

     ## Ticket
     <TICKET-ID or link, or "none">

     ## Solution doc
     <path, or "none">

     ## Changes
     - <bullet per notable change>

     ## Testing
     Test cases: <sheet path> - <n> passed, <n> failed, <n> need human review
     <failed cases and accepted reasons; human review cases and what to check>

     ## Code review
     <verdict; findings fixed; Minor findings and Questions left open>

     ## Notes for reviewers
     <risky areas, follow-ups, screenshots for UI changes>
     ```
7. Print the PR URL.

## Test sheet tool

`testsheet.py` in this skill's directory creates and updates the `.xlsx` sheet. Run it with `python3`; if that fails because `openpyxl` is missing, use `uv run` instead.

```sh
python3 <skill dir>/testsheet.py write <sheet.xlsx> <<'EOF'
[{"id": "TC-001", "requirement": "R1", "title": "...", "steps": ["...", "..."], "expected": "..."}]
EOF
python3 <skill dir>/testsheet.py dump <sheet.xlsx>
```

- `write` adds or updates rows by `id` and only changes the fields you pass, so reviewer notes are kept. Recording a result: `{"id": "TC-001", "status": "Passed", "actual": "<evidence>"}`; `last_run` and `attempts` are set automatically, and a third failure turns `Retrying` into `Failed`.
- `dump` prints status counts and every row as JSON.
- Never edit the `.xlsx` any other way. Reviewers edit it in Excel: the Status column is a dropdown and rows are coloured by status.
