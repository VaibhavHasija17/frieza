"""Run: python3 plugins/workflow/skills/dev/test_testsheet.py"""
import os
import tempfile

from openpyxl import load_workbook

from testsheet import columns_by_key, dump, write

path = os.path.join(tempfile.mkdtemp(), "cases.xlsx")

# create
write(path, [
    {"id": "TC-001", "requirement": "R1", "title": "Create order", "steps": ["Open form", "Submit"],
     "expected": "Order saved"},
    {"id": "TC-002", "requirement": "R1", "title": "Reject empty name", "expected": "400"},
])
data = dump(path)
assert data["counts"]["Not run"] == 2
assert data["rows"][0]["steps"] == "1. Open form\n2. Submit"

# a reviewer adds a note in Excel, then results are recorded: note survives, untouched fields survive
wb = load_workbook(path)
ws = wb["Test Cases"]
ws.cell(2, columns_by_key(ws)["notes"], "checked on staging")
wb.save(path)
write(path, [
    {"id": "TC-001", "status": "Passed", "actual": "201, row in orders"},
    {"id": "TC-002", "status": "Human review needed", "actual": "error copy needs PM sign-off"},
    {"id": "TC-003", "requirement": "R2", "title": "Totals", "expected": "sum", "status": "Failed"},
])
rows = {r["id"]: r for r in dump(path)["rows"]}
assert rows["TC-001"]["status"] == "Passed" and rows["TC-001"]["last_run"]
assert rows["TC-001"]["notes"] == "checked on staging"
assert rows["TC-001"]["title"] == "Create order"
assert rows["TC-001"]["attempts"] == 1
assert rows["TC-003"]["status"] == "Retrying" and rows["TC-003"]["attempts"] == 1
assert dump(path)["counts"] == {"Not run": 0, "Retrying": 1, "Passed": 1, "Failed": 0, "Human review needed": 1}

# three failed attempts before Failed
write(path, [{"id": "TC-003", "status": "Failed"}])
assert dump(path)["rows"][2]["status"] == "Retrying"
write(path, [{"id": "TC-003", "status": "Failed"}])
row = dump(path)["rows"][2]
assert row["status"] == "Failed" and row["attempts"] == 3

# fresh round after the developer steps in; passing on a retry
write(path, [{"id": "TC-003", "status": "Failed", "attempts": 0}])
assert dump(path)["rows"][2]["status"] == "Retrying"
write(path, [{"id": "TC-003", "status": "Passed"}])
row = dump(path)["rows"][2]
assert row["status"] == "Passed" and row["attempts"] == 2

# formatting survives reload
ws = load_workbook(path)["Test Cases"]
assert ws.data_validations.dataValidation and ws.conditional_formatting

print("ok")
