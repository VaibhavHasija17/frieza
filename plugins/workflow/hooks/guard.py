#!/usr/bin/env python3
"""PreToolUse guard. Reads hook JSON on stdin; exit 2 blocks the tool call and shows stderr to Claude."""
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys

# Projects override via .claude/settings.json: "env": {"WORKFLOW_PROTECTED_BRANCHES": "main,staging"}
PROTECTED = {b.strip() for b in os.environ.get("WORKFLOW_PROTECTED_BRANCHES", "main,master,develop").split(",") if b.strip()}
SECRET_FILE = re.compile(r"\.env(\..+)?")
SAFE_SECRET_SUFFIXES = (".example", ".sample", ".template")
RM_ROOT = re.compile(r"\brm\s+-\w*[rR]\w*\s+(/|/\*|~/?|\$HOME/?)(\s|$)")


def current_branch(cwd):
    try:
        return subprocess.run(["git", "-C", cwd, "branch", "--show-current"],
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ""


def check_push(segment, branch):
    try:
        args = shlex.split(segment)
    except ValueError:
        args = segment.split()
    args = args[args.index("push") + 1:]
    if any(a in ("-f", "--force") or a.startswith("--force=") for a in args):
        return "Force push blocked. Use --force-with-lease on your own branch."
    positional = [a for a in args if not a.startswith("-")]
    targets = {ref.split(":")[-1].lstrip("+") for ref in positional[1:]}
    if len(positional) < 2:
        targets.add(branch)  # bare `git push` / `git push origin` pushes the current branch
    hit = [t for t in targets if any(fnmatch.fnmatchcase(t, p) for p in PROTECTED)]
    if hit:
        return f"Direct push to {hit[0]} blocked. Push a feature branch and open a PR (/workflow:pr)."
    return None


def check(tool, inp, branch=""):
    if tool in ("Edit", "Write", "MultiEdit"):
        name = os.path.basename(inp.get("file_path", ""))
        if SECRET_FILE.fullmatch(name) and not name.endswith(SAFE_SECRET_SUFFIXES):
            return f"Editing {name} blocked: secrets file. Edit it by hand."
        return None
    if tool != "Bash":
        return None
    cmd = inp.get("command", "")
    if RM_ROOT.search(cmd):
        return "rm -r on / or home directory blocked."
    for segment in re.split(r"&&|\|\||;|\|", cmd):
        if re.search(r"\bgit(\s+-C\s+\S+)?\s+push\b", segment):
            reason = check_push(segment, branch)
            if reason:
                return reason
    return None


def main():
    data = json.load(sys.stdin)
    inp = data.get("tool_input", {})
    branch = current_branch(data.get("cwd", ".")) if "push" in inp.get("command", "") else ""
    reason = check(data.get("tool_name", ""), inp, branch)
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
