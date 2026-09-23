#!/usr/bin/env bash
# Install the EGo1 toolchain on the current Apple Silicon Mac.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TOOLCHAIN_ROOT="$ROOT/ego1-toolchain"

fail() {
  printf 'Installation stopped: %s\n' "$*" >&2
  exit 1
}

if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
  fail 'Run this installer on an Apple Silicon Mac in a native arm64 shell.'
fi
command -v xcode-select >/dev/null || fail 'Install Apple Command Line Tools with xcode-select --install.'
xcode-select -p >/dev/null 2>&1 || fail 'Install Apple Command Line Tools with xcode-select --install.'
command -v brew >/dev/null || fail 'Install Homebrew on this Mac from https://brew.sh, reopen Terminal, then rerun ./install.sh.'
command -v git >/dev/null || fail 'Git is required; install Apple Command Line Tools.'

BREW_PREFIX="$(brew --prefix)"
[[ -n "$BREW_PREFIX" ]] || fail 'Homebrew did not return an installation prefix.'
printf 'Installing Homebrew dependencies on this Mac (%s).\n' "$BREW_PREFIX"
brew install icarus-verilog verilator yosys openfpgaloader cmake ninja boost eigen python@3.11

PYTHON_311="$(brew --prefix python@3.11)/bin/python3.11"
[[ -x "$PYTHON_311" ]] || fail 'Homebrew Python 3.11 was not found.'
VENV="$TOOLCHAIN_ROOT/.venv"
if [[ ! -e "$VENV" ]]; then
  "$PYTHON_311" -m venv "$VENV"
elif [[ ! -x "$VENV/bin/python" ]]; then
  fail "The existing $VENV is incomplete. Inspect it before recreating it."
fi
"$VENV/bin/python" - "$VENV" <<'PY'
from pathlib import Path
import sys
expected = Path(sys.argv[1]).resolve()
if sys.version_info[:2] != (3, 11) or Path(sys.prefix).resolve() != expected:
    raise SystemExit(f"The existing environment is not Python 3.11 at {expected}; inspect it before reinstalling.")
PY
"$VENV/bin/python" -m pip install -r "$TOOLCHAIN_ROOT/requirements.lock.txt"

# Fetch source revisions recorded by this repository. Existing directories are
# never reset or overwritten; a mismatch requires a fresh checkout.
"$VENV/bin/python" - "$TOOLCHAIN_ROOT" <<'PY'
from pathlib import Path
import json
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
versions = json.loads((root / "versions.json").read_text())
src = root / "src"
src.mkdir(exist_ok=True)
for name in ("nextpnr", "prjxray", "prjxray-db"):
    repo = versions["repositories"][name]
    destination = src / name
    if not destination.exists():
        print(f"Cloning {name} from {repo['url']}", flush=True)
        subprocess.run(["git", "clone", "--recursive", repo["url"], str(destination)], check=True)
        subprocess.run(["git", "-C", str(destination), "checkout", "--detach", repo["commit"]], check=True)
        subprocess.run(["git", "-C", str(destination), "submodule", "update", "--init", "--recursive"], check=True)
    elif not (destination / ".git").exists():
        raise SystemExit(f"{destination} exists but is not a Git checkout; inspect it before retrying.")
    actual = subprocess.check_output(["git", "-C", str(destination), "rev-parse", "HEAD"], text=True).strip()
    if actual != repo["commit"]:
        raise SystemExit(f"{name} is at {actual}, expected {repo['commit']}; use a fresh project copy.")
    status = subprocess.check_output(["git", "-C", str(destination), "submodule", "status", "--recursive"], text=True)
    if any(line.startswith(("-", "+", "U")) for line in status.splitlines()):
        raise SystemExit(f"{name} has missing or mismatched submodules; inspect {destination}.")
    print(f"Pinned {name}: {actual}", flush=True)
PY

"$TOOLCHAIN_ROOT/rebuild.sh"
source "$TOOLCHAIN_ROOT/env.sh"
ego1-doctor
"$ROOT/vmake" blink all -f
printf '\nSoftware installation complete. Board detection and programming require a connected EGo1 and a separate request.\n'
