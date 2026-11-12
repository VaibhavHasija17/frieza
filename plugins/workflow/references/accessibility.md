# Accessibility checklist

For any change to a user interface. Target: WCAG 2.1 AA.

## Keyboard
- Every interactive element can be reached with Tab and used with Enter, Space, or arrow keys; Escape closes overlays.
- Focus order follows the visual order, and focus is always visible.
- Modals keep focus inside while open and return it when closed. No keyboard traps.

## Screen readers
- Images have `alt` text (`alt=""` for decorative ones). Icon-only buttons have `aria-label`.
- Every input has a label. Buttons and links say what they do ("Delete invoice", not "Click here").
- One `<h1>` per page; heading levels are not skipped.
- Content that changes without a page load is announced (`aria-live="polite"`, or `role="alert"` for errors).
- Use real elements: `<button>` for actions, `<a>` for navigation, `<table>` with `<th>` for tables.

## Visual
- Text contrast at least 4.5:1 (3:1 for large text); controls and focus rings at least 3:1.
- Colour is never the only signal (errors, status, required fields also use text or icons).
- Works at 200% zoom and on small screens. Touch targets at least 44 x 44 px.
- Nothing flashes more than 3 times per second.

## Forms
- Visible labels, required fields marked in text, errors next to the field and linked to it, an error summary that receives focus on submit.
- Known fields use `autocomplete` (`email`, `name`, `tel`, ...).

## How to check
- Keyboard only: complete the main task without a mouse.
- Automated: axe or Lighthouse accessibility audit (Playwright MCP can run the page). Automated tools find about a third of problems; keyboard and screen reader checks find the rest.
