#!/usr/bin/env bash
# Täglicher Second-Brain-Lauf: Agent sortiert den Eingang, Wrapper archiviert die Originale.
# Nutzung: daily-brain-curator.sh [live|dry]   (default: live)
set -euo pipefail

VAULT="${VAULT:-$HOME/SecondBrain}"
BASE="$HOME/second-brain/automation"
LOG_DIR="$BASE/logs"
STATE_DIR="$BASE/state"
LOCK_FILE="$STATE_DIR/run.lock"
LAST_RUN="$STATE_DIR/last-run"
PENDING="$STATE_DIR/pending-rerun"
UNPROCESSED="$STATE_DIR/unprocessed.txt"
MANIFEST="$VAULT/95_System/Agentenverwaltung/02_Aufgaben/_daily-manifest.json"
TODAY="$(date +%F)"
MODE="${1:-live}"
AGENT_TIMEOUT="${AGENT_TIMEOUT:-300}"

mkdir -p "$LOG_DIR" "$STATE_DIR"

# Nur ein Lauf gleichzeitig
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "another run in progress - exit"
  exit 0
fi

# Jeder Lauf hinterlässt einen Eintrag - auch bei Abbruch oder Fehler.
trap 'printf "%s mode=%s rc=%s pending=%s\n" "$(date -Is)" "$MODE" "${RC:-start}" "$([ -f "$PENDING" ] && echo 1 || echo 0)" >> "$LOG_DIR/wrapper.log"' EXIT

# Verarbeitbare Eingangsnotizen VOR dem Lauf explizit ermitteln.
# Der Agent bekommt die Liste mitgegeben, damit er nicht auf einen veralteten
# Verzeichnis-Eindruck angewiesen ist.
inbox_notes() {
  find "$VAULT/00_Eingang" -maxdepth 1 -type f -name '*.md' \
    ! -name 'README.md' ! -name 'Willkommen.md' ! -name '.*' \
    -printf '%f\n' 2>/dev/null | LC_ALL=C sort
}
BEFORE="$(inbox_notes)"

# Ein offener Retry-Marker bricht die "schon gelaufen"-Sperre.
if [ -f "$LAST_RUN" ] && [ "$(cat "$LAST_RUN")" = "$TODAY" ] \
   && [ ! -f "$PENDING" ] && [ "${FORCE:-0}" != "1" ] && [ "$MODE" = "live" ]; then
  echo "already ran on $TODAY - exit"
  exit 0
fi
rm -f "$PENDING" "$UNPROCESSED"

# Altes Manifest archivieren statt loeschen
if [ -f "$MANIFEST" ]; then
  mv -f "$MANIFEST" "$LOG_DIR/manifest-alt-$TODAY-$(date +%H%M%S).json"
fi

NOTE_LIST="$(printf '%s\n' "$BEFORE" | sed '/^$/d; s/^/- /')"
PROMPT="Fuehre deine taegliche Second-Brain-Pflege aus. Datum: $TODAY. Modus: $MODE.
Lies zuerst 00_Eingang/README.md, 95_System/Agentenverwaltung/README.md, 01_Start/Startseite.md und die Vorlagen in 90_Vorlagen/.
Die zum Laufbeginn im Eingang liegenden, zu verarbeitenden Dateien sind EXAKT diese:
${NOTE_LIST:-  (keine)}
Verarbeite jede einzelne und fuehre sie ALLE im Manifest auf - either unter moves oder unter unklaer. Nenne keine Datei, die nicht existiert, und ueberspringe keine aus der Liste.
Arbeite ausschliesslich mit relativen Pfaden ab dem Vault-Root.
Im Modus dry schreibe NUR das Manifest mit dryRun:true und einen Vorschlag in 95_System/Agentenverwaltung/02_Aufgaben/.
Im Modus live schreibe die einsortierten Notizen, das Manifest mit dryRun:false, die Tagesnotiz und das Protokoll gemaess deiner Rollenbeschreibung.
Melde zum Schluss deinen Handoff."

export VAULT
cd "$VAULT"
set +e
timeout "$AGENT_TIMEOUT" opencode run --agent brain-curator --auto \
  --title "Second Brain Daily $TODAY ($MODE)" \
  "$PROMPT" > "$LOG_DIR/$TODAY-$MODE.log" 2>&1
RC=$?
set -e

# Ein vorhandenes Manifest wird unabhängig vom Agenten-Exit-Code geprüft:
# opencode kann trotz erfolgreichem Handoff ungleich 0 zurückgeben.
HAD_MANIFEST=0
[ -f "$MANIFEST" ] && HAD_MANIFEST=1
if [ "$MODE" = "live" ] && [ "$HAD_MANIFEST" -eq 1 ]; then
  python3 "$BASE/apply_manifest.py" "$MANIFEST" >> "$LOG_DIR/$TODAY-$MODE.log" 2>&1 || true
elif [ "$MODE" = "live" ]; then
  echo "WARN: Agent hat kein Manifest geschrieben - keine Aenderung." >> "$LOG_DIR/$TODAY-$MODE.log"
fi
# apply_manifest verschiebt das Manifest bei Erfolg in logs/.
APPLIED=0
[ "$HAD_MANIFEST" -eq 1 ] && [ ! -f "$MANIFEST" ] && APPLIED=1

AFTER="$(inbox_notes)"
# Waehrend des Laufs neu dazugekommene Dateien gehoeren zum naechsten Lauf.
NEW="$(comm -13 <(printf '%s\n' "$BEFORE") <(printf '%s\n' "$AFTER"))"
# Vom Agenten vollstaendig uebergangene Dateien meldet apply_manifest.py.
if [ -n "$NEW" ] || { [ -f "$UNPROCESSED" ] && [ -s "$UNPROCESSED" ]; }; then
  {
    echo "Retry noetig - Eingang nicht vollstaendig abgedeckt."
    [ -n "$NEW" ] && echo "Neu seit Laufbeginn:" && printf '%s\n' "$NEW"
    [ -s "$UNPROCESSED" ] && echo "Nicht im Manifest erfasst:" && cat "$UNPROCESSED"
  } > "$PENDING"
  echo "WARN: Eingang nicht vollstaendig abgedeckt - Retry markiert." >> "$LOG_DIR/$TODAY-$MODE.log"
fi

if [ "$MODE" = "live" ] && [ ! -f "$PENDING" ] && { [ "$APPLIED" -eq 1 ] || [ -z "$BEFORE" ]; }; then
  echo "$TODAY" > "$LAST_RUN"
fi
echo "run complete rc=$RC log=$LOG_DIR/$TODAY-$MODE.log pending=$([ -f "$PENDING" ] && echo 1 || echo 0)"
exit "$RC"
