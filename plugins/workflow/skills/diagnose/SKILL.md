---
name: diagnose
description: Find the root cause of a bug, failing test, or performance regression with a disciplined loop - reproduce it with a fast command first, then minimise, hypothesise, confirm, fix, and add a regression test. Use when something is broken, throwing, failing, slow, or flaky, or when asked to debug or diagnose.
argument-hint: <bug report, error, failing test, or ticket>
---

# Diagnose

Bug: $ARGUMENTS

Inside `/workflow:dev`, run phases 1-4 in the Diagnose stage, and phases 5-6 in the Build stage after the branch exists. On its own, run all phases, stopping before phase 5 if the current branch is protected (default `main`, `master`, `develop`).

Redact secrets (tokens, passwords, keys) in every command and output you show: write `<REDACTED>`.

## 1. Reproduce with a command

**Do not theorise before this exists.** Build one command that goes red on *this* bug, and run it at least once. Options, best first:

1. A failing automated test at the closest seam (unit, integration, e2e).
2. A `curl` request against the local dev server.
3. A CLI run with a fixture input, compared to the expected output.
4. A Playwright script or the Playwright MCP tools asserting on the page.
5. A replayed captured request or payload.
6. A small throwaway script calling the failing code path directly.
7. For "sometimes wrong": a loop over many inputs or runs until it fails.
8. For "worked before": `git bisect run` with this command.

Make it **fast** (seconds), **specific** (checks the reported symptom, not "no crash"), and **repeatable**. For flaky bugs, raise the failure rate (loops, parallel runs, added load) until it fails often enough to work with.

If you cannot build one, stop. Say what you tried and ask for: access to an environment that shows the bug, a redacted log or captured request, or permission to add temporary logging.

## 2. Minimise

Confirm the command shows the *reported* failure, not a different nearby one. Strip inputs and steps until removing anything more makes it pass.

## 3. Hypothesise

List 2-4 possible causes, each with what you would see if it were true. Rank by likelihood and cost to check.

## 4. Confirm the cause

Check the top hypothesis with the cheapest evidence: logs, a debugger, a temporary print, a smaller test. Tag temporary code `DIAGNOSE-TEMP`. Move to the next hypothesis if it does not hold. Done when you can explain the cause from trigger to symptom.

Report: the reproduce command, the root cause with `file:line`, and the fix you propose.

## 5. Fix

Fix the cause, not the symptom. If the same cause can affect other callers or paths, fix it where they share code. Run the reproduce command: it must now pass.

## 6. Regression test and clean-up

- Turn the reproduce command into a permanent automated test if the project's test setup allows, so this bug cannot return unnoticed.
- Remove every `DIAGNOSE-TEMP` change.
- Run the project's lint and tests from `CLAUDE.md`.
