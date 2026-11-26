#!/usr/bin/env bash
# Install agents, commands and a minimal example vault. No network, no secrets.
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
OC_DIR="${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}"
VAULT="${VAULT:-$HOME/SecondBrain}"
CLIPBOARD_CAPTURE="${CLIPBOARD_CAPTURE:-0}"
STAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$OC_DIR/agents" "$OC_DIR/commands"

copy_with_backup() {
  local src="$1" dst="$2"
  [ -f "$dst" ] && cp -p "$dst" "$dst.bak-$STAMP"
  cp "$src" "$dst"
  printf 'installed %s\n' "$dst"
}

for f in "$SRC"/agents/*.md "$SRC"/commands/*.md; do
  [ -f "$f" ] || continue
  case "$f" in
    */agents/*) copy_with_backup "$f" "$OC_DIR/agents/$(basename "$f")" ;;
    */commands/*) copy_with_backup "$f" "$OC_DIR/commands/$(basename "$f")" ;;
  esac
done

if [ ! -d "$VAULT" ]; then
  mkdir -p "$(dirname "$VAULT")"
  cp -R "$SRC/examples/vault" "$VAULT"
  printf 'created example vault at %s\n' "$VAULT"
else
  printf 'kept existing vault at %s\n' "$VAULT"
fi

printf 'CLIPBOARD_CAPTURE=%s (set to 1 to enable)\n' "$CLIPBOARD_CAPTURE"
printf 'next: export VAULT=%q SECOND_BRAIN_HOME=%q\n' "$VAULT" "$SRC"
printf 'then: bash scripts/verify.sh\n'
