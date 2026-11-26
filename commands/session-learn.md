---
description: "Session-Lernen: aktuellen Verlauf exportieren, Lektionen und Protokoll im Second Brain ablegen, Health prüfen"
agent: supervisor
---

# Session-Lernen

Führe jetzt die Lernschleife für die aktuelle Session aus. $ARGUMENTS

1. Starte den Wrapper:
   `bash ~/second-brain/automation/brain-auto.sh --session-now`
2. Lies das JSON-Ergebnis und prüfe:
   - `queue` = 0 oder `steps.scribe` = `ok`
   - `lessons` und `protocols` sind plausibel
   - `health` = `ok` oder `warn` mit Begründung
3. Lies `95_System/Agentenverwaltung/04_Gedaechtnis_und_Kontext/_Lernindex.md` und fasse die neuen oder bestätigten Regeln in maximal 5 Zeilen zusammen.
4. Wenn `scribe` fehlschlägt: Ursache aus `~/second-brain/automation/logs/auto.log` und dem neuesten `scribe-*.log` nennen. Keine Geheimnisse ausgeben.
5. Melde knapp: Status, neue Lektionen, Protokollpfad, Health-Status, offene Punkte.

Nichts löschen, keine Rohdaten verändern, keine Geheimnisse ausgeben.
