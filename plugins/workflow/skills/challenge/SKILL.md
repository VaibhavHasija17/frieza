---
name: challenge
description: Have fresh, independent agents try to prove a design document, plan, root cause, or decision wrong before it is accepted, then fix what holds up. Documents get five parallel reviewers (simplicity, comprehension, design risk, codebase fit, implementation readiness); single claims get one adversarial reviewer. Use for solution docs, migrations, one-way-door changes, claims like "this is safe" or "this scales", or when asked to challenge, stress-test, or sanity-check something.
argument-hint: <document path, decision, or claim>
---

# Challenge

Target: $ARGUMENTS

A confident answer is not a correct one. Long sessions turn assumptions into "facts". This skill hands the work to reviewers with none of that context, whose job is to find what is wrong. You (with the context) decide what to do with their findings; the developer makes the trade-offs.

Use it for work that is costly to get wrong: design documents, changes that cross modules or services, changes that are hard to undo (migrations, public API changes, data deletion), and claims the code cannot prove by itself (safe, idempotent, scales, matches the spec). Not for renames, formatting, or obvious one-line changes.

Every reviewer must run as a subagent with a fresh context. If you cannot start subagents, stop and say so: a review in your own context is not independent.

## 1. Package the target without your reasoning

- **Artifact:** the document, plan, diff, or a 2-3 line statement of the decision or claim and what goes wrong if it is false.
- **Contract:** what it must satisfy: PRD requirements and confirmed Decisions, the quality bar (`docs/quality-bar.md`), relevant `CLAUDE.md` rules, constraints the developer stated.

Leave out your reasoning, the conversation, and why you believe it is right. Reviewers judge the artifact against the contract and the code, not your argument.

## 2. Pick the mode

- **Claim mode** (a decision, root cause, or claim): one reviewer, brief A.
- **Document mode** (solution doc, design, plan): five reviewers in parallel, briefs B1-B5, all started in one message.

Each reviewer gets the artifact, the contract, access to the codebase, and this common instruction:

> Find what is wrong; do not approve. Lead with problems. No praise, no restating the document. For each finding give: severity (Blocker, Major, or Minor), where (section or line), the concrete problem, and the code or contract line that shows it. If you find nothing significant, say so in one line. Under 400 words.

**A. Adversary (claim mode)**
> Try to prove this false. Check it against the contract and the actual code. Look for requirements it misses, false assumptions about existing code, ignored failure cases (errors, concurrency, partial failure, large data, old clients, rollback), and simpler approaches it overlooks.

**B1. Simplicity**
> Is anything here not needed now: features, options, abstractions, caching, queues, or configuration for imagined future needs? Search the codebase: does an existing module, helper, or library already do any of this? Does it fix the root problem or a symptom? Does it sink into code-level detail where the design should stay at interfaces and data flow?

**B2. Comprehension** - give this reviewer the artifact only, no codebase access.
> Read this as a new team member with no background. Flag every undefined term, acronym, or project-specific name; every step that assumes knowledge the document does not give; every sentence you had to read twice. Could you explain what is being built and why after one read?

**B3. Design risk**
> What fails at scale, under load, on partial failure, or with bad input? What does it cost to run? Which risks have no mitigation? Check security, data integrity, and rollback against the checklists in this plugin's `references/` folder (two folders up from this skill's directory): `security.md`, `performance.md`, `migrations.md`.

**B4. Codebase fit**
> Verify every claim about the existing code: files, functions, endpoints, tables, columns, and patterns it names must exist and behave as described. Flag claims that are wrong, patterns that differ from how the code actually does it, and existing code it should reuse but does not.

**B5. Implementation readiness**
> You are the engineer who will build this tomorrow. Do you know exactly what to change, where, and how? Flag every place that leaves a design decision to the implementer (an API shape, a data type, an error-handling strategy, a library choice), every vague step ("update the service"), and anything missing: schemas, migration steps, test expectations.

## 3. Sort the findings

Check each finding yourself against the artifact and the code:
- **Valid:** fix the artifact.
- **Invalid:** note in one line why (misread, or already handled, with where).
- **Needs a decision:** put it to the developer with your recommended answer.

## 4. Repeat or stop

Run another round on the fixed artifact if the last round had a Blocker or Major finding. In document mode, re-run only the reviewers whose areas changed. Stop when a round finds only Minor points, after 3 rounds, or when the developer says to stop.

## Report

What was challenged and in which mode; findings by outcome (fixed, rejected with reason, needs decision) and by reviewer; number of rounds. State problems plainly: no praise, no filler adjectives ("robust", "seamless").
