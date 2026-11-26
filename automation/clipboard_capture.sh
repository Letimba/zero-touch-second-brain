#!/usr/bin/env bash
# Capture the current Termux clipboard into the Second Brain.
# - raw copy: 00_Rohdaten/Zwischenablage/YYYY-MM-DD_HHMMSS__<hash8>.txt
# - inbox note: 00_Eingang/Zwischenablage-YYYY-MM-DD-HHMMSS.md
# Skips empty, short, duplicate and secret-looking content. Never prints content.
set -uo pipefail

VAULT="${VAULT:-$HOME/SecondBrain}"
BASE="$HOME/second-brain/automation"
STATE="$BASE/state"
LOGS="$BASE/logs"
RAW="$VAULT/00_Rohdaten/Zwischenablage"
INBOX="$VAULT/00_Eingang"
HASH_FILE="$STATE/clipboard.sha"
LOG="$LOGS/clipboard.log"

mkdir -p "$STATE" "$LOGS" "$RAW" "$INBOX"

if ! command -v termux-clipboard-get >/dev/null 2>&1; then
  printf '%s skip=no-termux-api\n' "$(date -Is)" >>"$LOG"
  exit 0
fi

TEXT="$(timeout 8 termux-clipboard-get 2>/dev/null)" || exit 0
# Strip NUL bytes only; keep the content otherwise unchanged.
TEXT="$(printf '%s' "$TEXT" | tr -d '\000')"
LEN=${#TEXT}

if [ "$LEN" -lt 20 ]; then
  exit 0
fi
if [ "$LEN" -gt 100000 ]; then
  TEXT="${TEXT:0:100000}"
  LEN=100000
fi

HASH="$(printf '%s' "$TEXT" | sha256sum | cut -d' ' -f1)"
if [ -f "$HASH_FILE" ] && [ "$(cat "$HASH_FILE" 2>/dev/null)" = "$HASH" ]; then
  exit 0
fi

# Never store credentials, tokens or private keys.
if printf '%s' "$TEXT" | grep -qE '(0t[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(password|passwd|token|secret|api[_-]?key)[[:space:]]*[:=][[:space:]]*[^[:space:]]{6,})'; then
  printf '%s' "$HASH" >"$HASH_FILE"
  printf '%s skipped=secret len=%s\n' "$(date -Is)" "$LEN" >>"$LOG"
  exit 0
fi

TS="$(date +%Y-%m-%d_%H%M%S)"
DATE="$(date +%F)"
RAW_FILE="$RAW/${TS}__${HASH:0:8}.txt"
NOTE="$INBOX/Zwischenablage-${TS}.md"

printf '%s' "$TEXT" >"$RAW_FILE"

FENCE='```'
case "$TEXT" in
  *'```'*) FENCE='````' ;;
esac

{
  printf '%s\n' '---'
  printf 'typ: quelle\n'
  printf 'status: draft\n'
  printf 'erstellt: %s\n' "$DATE"
  printf 'quelle: 00_Rohdaten/Zwischenablage/%s\n' "$(basename "$RAW_FILE")"
  printf 'tags: [zwischenablage, capture]\n'
  printf '%s\n' '---'
  printf '\n# Zwischenablage %s\n\n' "$TS"
  printf 'Automatisch aus der Zwischenablage erfasst. Rohkopie: `00_Rohdaten/Zwischenablage/%s`  \n' "$(basename "$RAW_FILE")"
  printf 'SHA-256: `%s`  \n' "$HASH"
  printf 'Kanal: [[Zwischenablage]]\n\n'
  printf '%s%s\n' "$FENCE" 'text'
  printf '%s\n' "$TEXT"
  printf '%s\n' "$FENCE"
} >"$NOTE"

printf '%s' "$HASH" >"$HASH_FILE"
printf '%s captured len=%s note=%s\n' "$(date -Is)" "$LEN" "$(basename "$NOTE")" >>"$LOG"
printf '{"captured": true, "chars": %s, "note": "%s"}\n' "$LEN" "$(basename "$NOTE")"
