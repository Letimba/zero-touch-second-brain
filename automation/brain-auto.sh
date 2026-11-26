#!/usr/bin/env bash
# Second Brain automation orchestrator.
#
# One run: clipboard capture -> session export -> brain-scribe -> inbox -> hygiene.
# Safe to call from the scheduler, from an interactive shell, or at session end.
#
# Usage:
#   brain-auto.sh                 normal run (export changed sessions, 1 digest, inbox if due)
#   brain-auto.sh --session-now   force-export the latest session and process its digest
#   brain-auto.sh --idle          hook-triggered run (latest session, 2 min idle)
#   brain-auto.sh --bg            shell catch-up run (same as normal)
#   brain-auto.sh --no-agent      clipboard + export + hygiene only
#   brain-auto.sh --clipboard-only
#   brain-auto.sh --force-inbox   ignore the 1-hour inbox throttle
#   brain-auto.sh --status        print last status and exit
set -uo pipefail

export PATH="${PREFIX:-$HOME/.local}/bin:$HOME/.local/bin:$HOME/bin:$PATH"

VAULT="${VAULT:-$HOME/SecondBrain}"
BASE="$HOME/second-brain/automation"
STATE="$BASE/state"
LOGS="$BASE/logs"
QUEUE="$BASE/queue"
LOCK="$STATE/auto.lock"
INDEX="$VAULT/95_System/Agentenverwaltung/04_Gedaechtnis_und_Kontext/_Lernindex.md"
LESSONS="$VAULT/95_System/Agentenverwaltung/04_Gedaechtnis_und_Kontext/Lektionen"
PROTOCOLS="$VAULT/95_System/Agentenverwaltung/04_Gedaechtnis_und_Kontext/Lernprotokolle"

mkdir -p "$STATE" "$LOGS" "$QUEUE"

MODE="full"
SESSION_NOW=0
NO_AGENT=0
CLIP_ONLY=0
STATUS_ONLY=0
FORCE_INBOX=0

for arg in "$@"; do
  case "$arg" in
    --session-now) MODE="session-now"; SESSION_NOW=1 ;;
    --idle) MODE="idle" ;;
    --bg) MODE="bg" ;;
    --no-agent) NO_AGENT=1 ;;
    --clipboard-only) CLIP_ONLY=1 ;;
    --force-inbox) FORCE_INBOX=1 ;;
    --status) STATUS_ONLY=1 ;;
    -h|--help)
      sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      printf 'unknown argument: %s\n' "$arg" >&2
      exit 2
      ;;
  esac
done

inbox_count() {
  find "$VAULT/00_Eingang" -maxdepth 1 -type f -name '*.md' \
    ! -name 'README.md' ! -name 'Willkommen.md' ! -name '.*' 2>/dev/null | wc -l | tr -d ' '
}

queue_count() {
  find "$QUEUE" -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' '
}

count_notes() {
  find "$1" -maxdepth 1 -type f -name '*.md' ! -name 'README.md' 2>/dev/null | wc -l | tr -d ' '
}

print_status() {
  printf '== last run ==\n'
  cat "$STATE/last-auto.json" 2>/dev/null || printf '(noch kein Lauf)\n'
  printf '\n== health ==\n'
  if [ -f "$STATE/health.json" ]; then
    jq '{status, inbox: .inbox_count, queue: .queue_count, lessons: .learning.lessons, protocols: .learning.protocols, top_rules: .learning.top_rules, secrets: (.secrets|length), scheduler: .scheduler.job_99101}' "$STATE/health.json" 2>/dev/null \
      || cat "$STATE/health.json"
  else
    printf '(noch keine Health-Daten)\n'
  fi
  printf '\n== queue ==\n'
  find "$QUEUE" -maxdepth 1 -type f -name '*.md' -printf '%f\n' 2>/dev/null | head -10
  printf 'pending=%s inbox=%s lessons=%s protocols=%s\n' \
    "$(queue_count)" "$(inbox_count)" "$(count_notes "$LESSONS")" "$(count_notes "$PROTOCOLS")"
}

if [ "$STATUS_ONLY" -eq 1 ]; then
  print_status
  exit 0
fi

# Only one orchestrator run at a time. The inbox wrapper uses its own lock.
exec 9>"$LOCK"
if ! flock -n 9; then
  printf '%s mode=%s skip=locked\n' "$(date -Is)" "$MODE" >>"$LOGS/auto.log"
  exit 0
fi

NOW="$(date +%s)"
printf '%s' "$NOW" >"$STATE/last-auto-attempt"
date -Is >"$STATE/last-auto-human"

CLIP_RC="skip"
EXPORT_RC="skip"
SCRIBE_RC="skip"
INBOX_RC="skip"
HYGIENE_RC="skip"
SESSION_QUEUE=""

log() {
  printf '%s mode=%s %s\n' "$(date -Is)" "$MODE" "$*" >>"$LOGS/auto.log"
}

# 1. Clipboard -> raw archive + inbox note.
if command -v termux-clipboard-get >/dev/null 2>&1; then
  bash "$BASE/clipboard_capture.sh" >>"$LOGS/auto.log" 2>&1
  CLIP_RC=$?
else
  CLIP_RC="missing"
fi

if [ "$CLIP_ONLY" -eq 1 ]; then
  log "clipboard-only rc=$CLIP_RC"
  exit 0
fi

# 2. Session export -> queue digests.
EXPORT_ARGS=(--limit 2 --idle-min 10)
if [ "$SESSION_NOW" -eq 1 ] || [ "$MODE" = "idle" ]; then
  EXPORT_ARGS=(--latest)
fi
EXPORT_OUT="$(python3 "$BASE/session_export.py" "${EXPORT_ARGS[@]}" 2>>"$LOGS/auto.log")"
EXPORT_RC=$?
if [ -n "$EXPORT_OUT" ]; then
  printf '%s\n' "$EXPORT_OUT" >>"$LOGS/auto.log"
fi
if [ "$SESSION_NOW" -eq 1 ] && [ -n "$EXPORT_OUT" ]; then
  SESSION_QUEUE="$(printf '%s' "$EXPORT_OUT" | jq -r '.exported[0].queue // empty' 2>/dev/null)"
fi

# 3. One digest -> brain-scribe.
redact_stream() {
  sed -E \
    -e 's/(0t[A-Za-z0-9_-]{20,})/[REDACTED]/g' \
    -e 's/(sk-[A-Za-z0-9_-]{20,})/[REDACTED]/g' \
    -e 's/(ghp_[A-Za-z0-9]{20,})/[REDACTED]/g' \
    -e 's/(github_pat_[A-Za-z0-9_]{20,})/[REDACTED]/g' \
    -e 's/(AKIA[0-9A-Z]{16})/[REDACTED]/g'
}

pick_digest() {
  if [ -n "$SESSION_QUEUE" ] && [ -f "$SESSION_QUEUE" ]; then
    printf '%s\n' "$SESSION_QUEUE"
    return 0
  fi
  find "$QUEUE" -maxdepth 1 -type f -name '*.md' -printf '%T@ %p\n' 2>/dev/null \
    | sort -n | head -1 | cut -d' ' -f2-
}

run_scribe() {
  local digest="$1"
  [ -n "$digest" ] && [ -f "$digest" ] || { SCRIBE_RC="empty"; return 0; }

  local before_index before_lessons before_protocols after_index after_lessons after_protocols
  before_index="$(stat -c %Y "$INDEX" 2>/dev/null || echo 0)"
  before_lessons="$(count_notes "$LESSONS")"
  before_protocols="$(count_notes "$PROTOCOLS")"

  local out="$LOGS/scribe-$(date +%Y%m%d-%H%M%S).log"
  local prompt
  prompt="Führe deinen Auftrag als brain-scribe aus.
Digest: $digest
Vault: $VAULT
Lies den Digest vollständig, prüfe bestehende Lektionen und den Lernindex auf Duplikate, lege maximal 5 neue Lektionen und genau ein Protokoll an und aktualisiere _Lernindex.md.
Keine Geheimnisse, keine Chatverläufe. Melde am Ende deinen Handoff."

  (
    cd "$VAULT" || exit 1
    timeout "${SCRIBE_TIMEOUT:-900}" opencode run --agent brain-scribe --auto \
      --title "Brain-Scribe $(basename "$digest" .md)" \
      "$prompt"
  ) >"$out" 2>&1
  local rc=$?

  after_index="$(stat -c %Y "$INDEX" 2>/dev/null || echo 0)"
  after_lessons="$(count_notes "$LESSONS")"
  after_protocols="$(count_notes "$PROTOCOLS")"

  if [ "$rc" -eq 0 ] || [ "$after_index" != "$before_index" ] \
     || [ "$after_lessons" != "$before_lessons" ] \
     || [ "$after_protocols" != "$before_protocols" ]; then
    local done_dir="$QUEUE/done/$(date +%F)"
    mkdir -p "$done_dir"
    mv -f "$digest" "$done_dir/"
    SCRIBE_RC="ok"
    log "scribe ok rc=$rc digest=$(basename "$digest") out=$(basename "$out")"
  else
    SCRIBE_RC="error:$rc"
    log "scribe failed rc=$rc digest=$(basename "$digest") out=$(basename "$out")"
  fi

  # Keep a redacted tail for the shared log; the full log stays local.
  if [ -f "$out" ]; then
    redact_stream <"$out" | tail -20 >>"$LOGS/auto.log"
  fi
}

if [ "$NO_AGENT" -eq 1 ]; then
  SCRIBE_RC="skipped"
else
  DIGEST="$(pick_digest)"
  if [ -n "$DIGEST" ]; then
    run_scribe "$DIGEST"
  else
    SCRIBE_RC="empty"
  fi
fi

# 4. Inbox -> brain-curator, at most once per hour (unless forced).
if [ "$NO_AGENT" -eq 1 ]; then
  INBOX_RC="skipped"
else
  INBOX_NOW="$(inbox_count)"
  LAST_INBOX="$(cat "$STATE/inbox-last-attempt" 2>/dev/null || echo 0)"
  case "$LAST_INBOX" in *[!0-9]*) LAST_INBOX=0 ;; esac
  if [ "$INBOX_NOW" -eq 0 ]; then
    INBOX_RC="empty"
  elif [ "$FORCE_INBOX" -ne 1 ] && [ $((NOW - LAST_INBOX)) -lt "${INBOX_INTERVAL:-3600}" ]; then
    INBOX_RC="throttled"
  else
    printf '%s' "$NOW" >"$STATE/inbox-last-attempt"
    FORCE=1 timeout 600 bash "$BASE/daily-brain-curator.sh" live >>"$LOGS/auto.log" 2>&1
    INBOX_RC=$?
    if [ "$INBOX_RC" -eq 0 ] && [ ! -f "$STATE/pending-rerun" ]; then
      printf '%s' "$NOW" >"$STATE/inbox-last-success"
    fi
  fi
fi

# 5. Hygiene and report.
python3 "$BASE/brain_hygiene.py" >>"$LOGS/auto.log" 2>&1
HYGIENE_RC=$?

HEALTH_STATUS="unknown"
[ -f "$STATE/health.json" ] && HEALTH_STATUS="$(jq -r '.status // "unknown"' "$STATE/health.json" 2>/dev/null)"

TMP_STATUS="$STATE/last-auto.json.tmp"
jq -n \
  --arg ts "$(date -Is)" \
  --arg mode "$MODE" \
  --arg clipboard "$CLIP_RC" \
  --arg export "$EXPORT_RC" \
  --arg scribe "$SCRIBE_RC" \
  --arg inbox "$INBOX_RC" \
  --arg hygiene "$HYGIENE_RC" \
  --arg health "$HEALTH_STATUS" \
  --argjson queue "$(queue_count)" \
  --argjson inbox_count "$(inbox_count)" \
  --argjson lessons "$(count_notes "$LESSONS")" \
  --argjson protocols "$(count_notes "$PROTOCOLS")" \
  '{
    timestamp: $ts,
    mode: $mode,
    steps: {
      clipboard: $clipboard,
      export: $export,
      scribe: $scribe,
      inbox: $inbox,
      hygiene: $hygiene
    },
    health: $health,
    queue: $queue,
    inbox: $inbox_count,
    lessons: $lessons,
    protocols: $protocols
  }' >"$TMP_STATUS" 2>/dev/null && mv -f "$TMP_STATUS" "$STATE/last-auto.json"

log "done clip=$CLIP_RC export=$EXPORT_RC scribe=$SCRIBE_RC inbox=$INBOX_RC hygiene=$HYGIENE_RC health=$HEALTH_STATUS queue=$(queue_count) inbox=$(inbox_count)"

if [ -f "$STATE/last-auto.json" ]; then
  cat "$STATE/last-auto.json"
else
  printf '{"mode":"%s","clipboard":"%s","export":"%s","scribe":"%s","inbox":"%s","hygiene":"%s"}\n' \
    "$MODE" "$CLIP_RC" "$EXPORT_RC" "$SCRIBE_RC" "$INBOX_RC" "$HYGIENE_RC"
fi
