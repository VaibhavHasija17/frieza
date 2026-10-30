#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["openpyxl"]
# ///
"""Test case sheet for /workflow:dev.

  testsheet.py write <file.xlsx> < cases.json   upsert rows by "id"; creates the file if missing
  testsheet.py dump <file.xlsx>                 print status counts and all rows as JSON

cases.json is a list of objects using the keys in COLUMNS. Only the keys given are written,
so updating a status leaves everything else (including reviewer notes) untouched.

Writing "Passed" or "Failed" counts one attempt. A failure only becomes "Failed" on attempt
MAX_ATTEMPTS; before that the case is "Retrying". Pass "attempts": 0 to start a fresh round.
Run with `python3` when openpyxl is installed, otherwise `uv run` (installs it).
"""
import datetime
import json
import os
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

COLUMNS = [  # (json key, header, width)
    ("id", "ID", 9),
    ("requirement", "Req", 7),
    ("title", "Test case", 32),
    ("type", "Type", 12),
    ("priority", "Priority", 9),
    ("preconditions", "Preconditions", 28),
    ("steps", "Steps", 40),
    ("test_data", "Test data", 24),
    ("expected", "Expected result", 36),
    ("automated_test", "Automated test", 28),
    ("status", "Status", 20),
    ("attempts", "Attempts", 9),
    ("actual", "Actual result / evidence", 40),
    ("notes", "Reviewer notes", 30),
    ("last_run", "Last run", 11),
]
KEYS = [key for key, _, _ in COLUMNS]
HEADER_TO_KEY = {header: key for key, header, _ in COLUMNS}
STATUSES = ["Not run", "Retrying", "Passed", "Failed", "Human review needed"]
COLORS = {"Retrying": "DDEBF7", "Passed": "C6EFCE", "Failed": "FFC7CE", "Human review needed": "FFEB9C"}
MAX_ATTEMPTS = 3
SHEET = "Test Cases"
MAX_ROW = 1000  # ponytail: dropdown and colours cover rows 2-1000; raise if a feature needs more cases


def new_workbook():
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET
    ws.append([header for _, header, _ in COLUMNS])
    for i, (_, _, width) in enumerate(COLUMNS, 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", start_color="305496", end_color="305496")
    ws.freeze_panes = "C2"

    status_col = get_column_letter(KEYS.index("status") + 1)
    last_col = get_column_letter(len(COLUMNS))
    dropdown = DataValidation(type="list", formula1='"%s"' % ",".join(STATUSES))
    dropdown.add("%s2:%s%d" % (status_col, status_col, MAX_ROW))
    ws.add_data_validation(dropdown)
    for status, color in COLORS.items():
        ws.conditional_formatting.add(
            "A2:%s%d" % (last_col, MAX_ROW),
            FormulaRule(formula=['$%s2="%s"' % (status_col, status)],
                        fill=PatternFill("solid", start_color=color, end_color=color)))

    # Formulas, so counts stay right when reviewers change statuses in Excel.
    summary = wb.create_sheet("Summary")
    summary.append(["Status", "Count"])
    for status in STATUSES:
        summary.append([status, "=COUNTIF('%s'!%s:%s,\"%s\")" % (SHEET, status_col, status_col, status)])
    summary.append(["Total", "=COUNTA('%s'!A:A)-1" % SHEET])
    for cell in summary[1]:
        cell.font = Font(bold=True)
    summary.column_dimensions["A"].width = 22
    return wb


def columns_by_key(ws):
    """Map json key -> column number from the header row, so reordered columns still work."""
    return {HEADER_TO_KEY[c.value]: c.column for c in ws[1] if c.value in HEADER_TO_KEY}


def write(path, cases):
    wb = load_workbook(path) if os.path.exists(path) else new_workbook()
    ws = wb[SHEET]
    cols = columns_by_key(ws)
    rows = {ws.cell(r, cols["id"]).value: r for r in range(2, ws.max_row + 1) if ws.cell(r, cols["id"]).value}
    today = datetime.date.today().isoformat()

    for case in cases:
        if "id" not in case:
            sys.exit("every case needs an id: %r" % case)
        unknown = set(case) - set(KEYS)
        if unknown:
            sys.exit("unknown fields %s; allowed: %s" % (sorted(unknown), KEYS))
        if case.get("status", "Not run") not in STATUSES:
            sys.exit("bad status %r; allowed: %s" % (case["status"], STATUSES))

        row = rows.get(case["id"])
        if row is None:
            row = rows[case["id"]] = ws.max_row + 1
            case = dict({"status": "Not run"}, **case)
        if case.get("status", "Not run") != "Not run":
            case.setdefault("last_run", today)
        if case.get("status") in ("Passed", "Failed", "Retrying"):
            previous = case["attempts"] if "attempts" in case else ws.cell(row, cols["attempts"]).value
            case["attempts"] = (previous or 0) + 1
            if case["status"] != "Passed":
                case["status"] = "Failed" if case["attempts"] >= MAX_ATTEMPTS else "Retrying"
                if case["status"] == "Retrying":
                    print("%s: attempt %d/%d failed - fix the cause and re-run"
                          % (case["id"], case["attempts"], MAX_ATTEMPTS), file=sys.stderr)

        for key, value in case.items():
            if isinstance(value, list):
                value = "\n".join("%d. %s" % (i, v) for i, v in enumerate(value, 1))
            cell = ws.cell(row, cols[key], value)
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(ws.max_column), ws.max_row)
    wb.save(path)


def dump(path):
    ws = load_workbook(path)[SHEET]
    cols = columns_by_key(ws)
    rows = []
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, cols["id"]).value:
            rows.append({key: ws.cell(r, col).value for key, col in cols.items()})
    counts = {status: sum(row.get("status") == status for row in rows) for status in STATUSES}
    return {"counts": counts, "rows": rows}


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("write", "dump"):
        sys.exit(__doc__)
    if sys.argv[1] == "write":
        write(sys.argv[2], json.load(sys.stdin))
    print(json.dumps(dump(sys.argv[2]), indent=2, default=str))
