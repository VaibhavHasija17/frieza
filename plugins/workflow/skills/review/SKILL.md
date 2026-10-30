---
name: review
description: Company code review - review the current branch, a pull request, or specific files for bugs, security, data, API, test, and convention problems, checked against CLAUDE.md and the solution doc. Use when asked to review code, a diff, a branch, or a PR, and as the review stage of /workflow:dev.
argument-hint: [PR number or URL | file paths | nothing for the current branch]
---

# Code review

Target: $ARGUMENTS

Read-only: report findings, do not edit code unless the developer asks for fixes. Never post comments to a PR unless asked.

## 1. Get the changes

- **Nothing given:** the current branch against the default branch, including uncommitted work: `git diff $(git merge-base origin/<default> HEAD)`. Find `<default>` with `git symbolic-ref --short refs/remotes/origin/HEAD`.
- **PR number or URL:** `gh pr view <n>` for the description and `gh pr diff <n>` for the changes. To read full files at the PR's version, `git fetch origin pull/<n>/head` and `git show FETCH_HEAD:<path>`. Do not check out or create branches.
- **File paths:** review those files as they are now.

## 2. Gather context

- `CLAUDE.md` and the module `CLAUDE.md` files of the changed areas: the conventions the code must follow.
- The solution doc and test sheet for this work, if any (solution docs folder from the **Workflow** section of `CLAUDE.md`, default `docs/solutions/`; match the branch's ticket or slug). The code should do what the doc says and nothing more.
- For each changed function or file, read the surrounding code, its callers, and the code it calls. A diff alone hides most real bugs.

For a large change, split it by area across parallel subagents, then verify their findings yourself.

## 3. Review

Look for problems in this order of importance:

1. **Correctness:** logic errors, wrong conditions, unhandled edge cases (empty, null, zero, duplicates, large inputs), error paths that are swallowed or leave partial state, race conditions, wrong async handling.
2. **Security:** missing auth or permission checks, injection (SQL, command, template, path), unvalidated input at trust boundaries, secrets in code, sensitive data in logs or responses.
3. **Data:** migrations that cannot be rolled back or lock large tables, missing indexes for new queries, N+1 queries, missing transactions around multi-step writes, backward-incompatible schema changes.
4. **API contract:** changes that break existing clients, responses that differ from the solution doc, inconsistent error formats.
5. **Tests:** requirements or branches with no test, tests that cannot fail, mocked-away logic under test.
6. **Conventions and reuse:** patterns from `CLAUDE.md` not followed, new code that duplicates an existing helper, code in the wrong layer.
7. **Leftovers and complexity:** debug code, commented-out code, TODOs without a ticket, abstractions with one use, dead code.

Skip formatting and style that a linter or formatter handles.

## 4. Verify every finding

Before reporting a finding, confirm it against the code: trace the inputs that reach it and check whether something elsewhere already handles it. Each finding needs a concrete scenario (input or state, then the wrong result). Drop anything you cannot back with a scenario, or mark it **Question** if it needs the author's knowledge.

## 5. Report

Group findings by severity, most severe first:

- **Critical** - must fix before merge: bugs that produce wrong results, security holes, data loss or corruption.
- **Major** - should fix before merge: missing tests for requirements, breaking API changes, performance problems at expected load, convention violations that will spread.
- **Minor** - worth fixing, not blocking.
- **Question** - needs the author's input.

One entry per finding:

```
[Critical] path/to/file.ts:42 - <problem in one line>
  Scenario: <input or state> -> <wrong result>
  Fix: <specific change>
```

End with:
- **Verdict:** `Approve`, `Approve with minor fixes`, or `Changes requested` (any Critical or Major finding).
- **Solution doc check:** implemented as designed, or the gaps found.
- Counts per severity. If there are no findings, say so plainly.

For a PR target, offer to post the findings as a PR review (`gh pr review <n> --comment --body-file <file>`) and do it only if the developer agrees.
