---
typ: lektion
status: aktiv
erstellt: 2026-11-27
prioritaet: P1
bestaetigt_am: [2026-11-27]
tags: [verifikation]
---
# Abschluss nur mit Evidenz

## Regel
Ein Fix oder Feature gilt erst mit einem ausgeführten Befehl und dessen echtem
Ergebnis als fertig.

## Warum
Ein grüner Build sagt nichts über Laufzeitverhalten, Datenintegrität oder
Security aus.

## Anwendung
Testbefehl, Ergebnis und nicht geprüfte Lücken im Handoff nennen.

## Grenzen
Bei fehlender Testumgebung die Lücke explizit ausweisen, nicht schweigen.
