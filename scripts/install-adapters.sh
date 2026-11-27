#!/usr/bin/env bash
# Install learning-loop context for additional coding agents. No network, no secrets.
# Usage: bash scripts/install-adapters.sh claude|codex|gemini|cursor|windsurf [project-dir]
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
CLI="${1:-}"
PROJECT="${2:-}"
VAULT="${VAULT:-$HOME/SecondBrain}"
STAMP="$(date +%Y%m%d-%H%M%S)"

case "$CLI" in
  claude|codex|gemini|cursor|windsurf) ;;
  *) printf 'usage: %s <claude|codex|gemini|cursor|windsurf> [project-dir]\n' "$0" >&2; exit 2 ;;
esac

render() {
  sed -e "s|{{VAULT}}|$VAULT|g" -e "s|{{SRC}}|$SRC|g" \
    "$SRC/adapters/common/LEARNING-LOOP.md"
}

write_backup() {
  local content="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  [ -f "$dst" ] && cp -p "$dst" "$dst.bak-$STAMP"
  printf '%s\n' "$content" > "$dst"
  printf 'installed %s\n' "$dst"
}

CTX="$(render)"

case "$CLI" in
  claude)
    write_backup "$CTX" "$HOME/.claude/AGENTS.md"
    mkdir -p "$HOME/.claude/agents"
    for a in brain-scribe brain-curator; do
      src="$SRC/agents/$a.md"; dst="$HOME/.claude/agents/$a.md"
      [ -f "$src" ] || continue
      if grep -q '^name:' "$src"; then cp "$src" "$dst"; else
        { printf 'name: %s\n' "$a"; cat "$src"; } > "$dst"
      fi
      printf 'installed %s\n' "$dst"
    done
    ;;
  codex)
    write_backup "$CTX" "$HOME/.codex/AGENTS.md"
    mkdir -p "$HOME/.codex/skills/zero-touch-second-brain"
    write_backup "$(printf '%s\n' '---' 'name: zero-touch-second-brain' 'description: Session learning loop and vault hygiene for a plain-Markdown second brain.' '---' '' "$CTX")" \
      "$HOME/.codex/skills/zero-touch-second-brain/SKILL.md"
    ;;
  gemini)
    write_backup "$CTX" "$HOME/.gemini/GEMINI.md"
    ;;
  cursor)
    [ -n "$PROJECT" ] || { printf 'cursor needs a project dir\n' >&2; exit 2; }
    write_backup "$CTX" "$PROJECT/AGENTS.md"
    write_backup "$(printf '%s\n' '---' 'description: Second Brain learning loop for agent sessions' 'globs: **/*' 'alwaysApply: true' '---' '' "$CTX")" \
      "$PROJECT/.cursor/rules/zero-touch-second-brain.mdc"
    ;;
  windsurf)
    write_backup "$CTX" "$HOME/.codeium/windsurf/memories/global_rules.md"
    if [ -n "$PROJECT" ]; then
      write_backup "$(printf '%s\n' '---' 'trigger: always_on' '---' '' "$CTX")" \
        "$PROJECT/.windsurf/rules/zero-touch-second-brain.md"
    fi
    ;;
esac

printf 'done. Restart the CLI if it does not reload context files.\n'
