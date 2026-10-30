"""Run: python3 plugins/workflow/hooks/test_guard.py"""
from guard import check


def bash(cmd, branch="feat/x"):
    return check("Bash", {"command": cmd}, branch)


# blocked
assert bash("git push --force origin feat/x")
assert bash("git push -f")
assert bash("git push origin main")
assert bash("git push origin HEAD:master")
assert bash("git push", branch="main")
assert bash("git push -u origin", branch="develop")
assert bash("npm test && git push origin +main")
assert bash("rm -rf /")
assert bash("rm -rf ~")
assert check("Write", {"file_path": "/app/.env"})
assert check("Edit", {"file_path": "/app/.env.production"})

# allowed
assert not bash("git push -u origin feat/x")
assert not bash("git push --force-with-lease")
assert not bash("git push origin feat/main-menu")
assert not bash("git push origin feat/x", branch="main")
assert not bash("rm -rf ./build")
assert not bash("git log main..HEAD")
assert not bash("git stash push -m wip", branch="main")
assert not check("Write", {"file_path": "/app/.env.example"})
assert not check("Read", {"file_path": "/app/.env"})

# project override with a glob
import guard
guard.PROTECTED = {"staging", "release/*"}
assert bash("git push origin release/2.1")
assert bash("git push", branch="staging")
assert not bash("git push origin main")

print("ok")
