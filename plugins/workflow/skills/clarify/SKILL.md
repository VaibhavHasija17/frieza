---
name: clarify
description: Interview the developer in rounds until every decision in a PRD, plan, ticket, or idea is settled, before any design or code is written. Use when requirements are unclear or incomplete, before writing a solution doc, or when asked to clarify, grill, or poke holes in a plan.
argument-hint: <PRD, plan, ticket, or idea>
---

# Clarify

Input: $ARGUMENTS

Goal: a shared understanding of what to build, with nothing silently assumed. No design docs or code in this skill.

## How it works

1. **Read first.** Read the input, `CLAUDE.md`, and the code it touches. Facts are your job: anything you can find in the code, docs, git history, or tools, look up yourself (use an Explore subagent for broad searches). Never ask the developer something you could find.
2. **Map the decisions.** List the open decisions as a tree: each decision unlocks the ones that depend on it. Typical branches: scope and non-goals, user roles and permissions, data and its lifecycle, edge cases and errors, API and UI behaviour, migration of existing data, rollout, and what "done" looks like.
3. **Ask in rounds.** Each round asks every decision that can be answered *now*: its prerequisites are settled. A question that depends on another question in the same round waits for the next round. Format:

   ```
   **Q1 - <short title>**: <the question, with the options and their trade-offs if useful>
   Recommended: <your answer, and why in one line>

   **Q2 - ...**
   ```

   Word each question so that "yes" accepts your recommendation. Number questions across rounds (Q1, Q2, ... Q7) so answers like "yes to all except Q3" work.
4. **Wait.** Decisions belong to the developer. After each round, update the tree from the answers and ask the next round.
5. **Route what they cannot answer.** If a question needs someone else (PM, design, another team), mark it `For: <role>` and keep going with the rest. It ends up in the solution doc's **Open questions**.
6. **Finish** when no decision is left open. Reply with a numbered **Decisions** list (one line each, in the developer's words where possible) and the **Open questions** for others. Ask the developer to confirm it before anything is built on it.

## Rules

- Ask only questions whose answer changes what gets built. Skip trivia and anything the codebase already decides.
- Use the project's own terms, from `CLAUDE.md` and the code.
- Plain, short questions. No essays.
- Do not just agree. If an answer creates a conflict or a risk, say so and ask again. No praise for answers ("great question", "good call").
- Do not restate the developer's framing as fact; check it against the code first.
