#!/data/data/com.termux/files/usr/bin/bash
# Termux scheduler wrapper.
# /usr/bin/env does not exist on Android/Termux, so the portable scripts use
# `#!/usr/bin/env bash` for Linux/macOS and are invoked through bash here.
set -uo pipefail

BASE="${SECOND_BRAIN_HOME:-$HOME/zero-touch-second-brain}"
exec "$PREFIX/bin/bash" "$BASE/automation/brain-auto.sh" --bg "$@"
