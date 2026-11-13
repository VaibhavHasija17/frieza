---
name: review
description: Company code review - review the current branch, a pull request, or specific files along three separate axes (correctness and safety, project standards, match with the spec), each run by an isolated read-only agent with no conversation context, with every finding verified. Use when asked to review code, a diff, a branch, or a PR, and as the review stage of /workflow:dev.
argument-hint: [PR number or URL | file paths | nothing for the current branch]
---

# Code review

Target: $ARGUMENTS

Read-only: report findings, do not edit code unless the developer asks for fixes. Never post comments to a PR unless asked.

Tone: lead with problems; no praise, no filler adjectives ("robust", "clean", "seamless"). Agree that something is fine only after checking it.

## 1. Pin the changes

- **Nothing given:** the current branch against the default branch, including uncommitted work: `git diff $(git merge-base origin/<default> HEAD)`. Find `<default>` with `git symbolic-ref --short refs/remotes/origin/HEAD`.
- **PR number or URL:** `gh pr view <n>` for the description and `gh pr diff <n>` for the changes. To read full files at the PR's version, `git fetch origin pull/<n>/head` and `git show FETCH_HEAD:<path>`. Do not check out or create branches.
- **File paths:** review those files as they are now.

Check the diff is not empty before going further.

## 2. Collect the sources

- **Standards:** `CLAUDE.md`, the module `CLAUDE.md` files of the changed areas, `docs/quality-bar.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, and any other doc that says how code is written here.
- **Spec:** the solution doc and test sheet for this work (solution docs folder from the **Workflow** section of `CLAUDE.md`, default `docs/solutions/`, matching the branch's ticket or slug), the PR description, or the ticket. If there is none, ask; if there really is none, skip the Spec axis and say so.

## 3. Run three isolated reviewers in parallel

Each reviewer is a plugin agent that starts with a blank context: no chat history, no knowledge of how or why the code was written. Start all three in one message with the Agent tool:

| Reviewer | `subagent_type` | Checks |
|----------|-----------------|--------|
| Correctness and safety | `workflow:review-correctness` | Bugs, security, data and migrations, performance, against the checklists |
| Standards | `workflow:review-standards` | Project rules, quality bar, code smells, leftovers, stale `CLAUDE.md` files |
| Spec | `workflow:review-spec` | Missing, extra, wrong, or untested requirements |

Never use a `fork` subagent or any agent that inherits this conversation. If the `workflow:review-*` agents are not available, use `general-purpose` agents and tell each to follow the instructions in this plugin's `agents/review-<axis>.md` (two folders up from this skill's directory). If no subagents can be started, stop and say so: a review in this context is not independent.

**What each reviewer's prompt contains - and nothing else:**
- The repository path and the exact diff command (or PR number, or file list) from step 1.
- The absolute paths of its sources from step 2: standards files for Standards; the spec files for Spec; for Correctness, the absolute path of this plugin's `references/` folder (two folders up from this skill's directory).
- For Spec, if there is a test sheet: the command `python3 <absolute path to this plugin>/skills/dev/testsheet.py dump <sheet>` (or `uv run` instead of `python3` if `openpyxl` is missing).

**Never put in a reviewer's prompt:** the conversation or a summary of it, what was built or why, the developer's or your own reasoning, claims that something is correct or already tested, earlier review findings, or what you expect them to find. If a reviewer needs to know intent, that must come from the spec files, not from you.

## 4. Verify every finding

For each finding the reviewers return, confirm it yourself in the code: trace the inputs that reach it and check whether something elsewhere already handles it. Each finding needs a concrete scenario (input or state, then the wrong result). Drop what you cannot back up, or mark it **Question** if it needs the author's knowledge.

**Red flags**

| If you think... | Then... |
|-----------------|---------|
| "The tests pass, so it's correct" | Tests only cover what someone thought of. Read the code paths. |
| "It's a small diff, a quick look is enough" | Small diffs in auth, money, or data code need the full review. |
| "The author probably handled this elsewhere" | Find where. If you cannot, it is a finding or a Question. |
| "Too many findings, I'll drop the minor ones" | Report them as Minor; the developer decides. |

## 5. Report

Keep the three axes separate, so a pass on one cannot hide a failure on another. Under `## Correctness and safety`, `## Standards`, and `## Spec`, list findings most severe first:

```
[Critical] path/to/file.ts:42 - <problem in one line>
  Scenario: <input or state> -> <wrong result>
  Fix: <specific change>
```

- **Critical** - must fix before merge: wrong results, security holes, data loss or corruption, a required feature missing.
- **Major** - should fix before merge: missing tests for requirements, breaking API changes, performance problems at expected load, rule breaks that will spread.
- **Minor** - worth fixing, not blocking (most smells).
- **Question** - needs the author's input.
- **Needs validation** - a real problem only if something outside the code is true (production config, infrastructure, a third-party setting). Say exactly what someone should check. Does not block on its own.

**Security findings are optional.** List findings tagged `[Security]` together under `## Security (your decision)`, with their severity. The developer decides, finding by finding, whether to fix each one. They never decide the verdict on their own.

End with one line per axis (counts and worst finding), then the **Verdict**, ignoring `[Security]` findings: `Changes requested` if any axis has a Critical or Major finding, `Approve with minor fixes` if only Minor findings or Questions remain, otherwise `Approve`.

For a PR target, offer to post the findings as a PR review (`gh pr review <n> --comment --body-file <file>`) and do it only if the developer agrees.
