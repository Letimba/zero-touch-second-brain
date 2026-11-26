---
description: "Second-Brain-Status: letzter Automationslauf, Health, Queue, Eingang, Scheduler"
agent: supervisor
---

# Brain-Status

Führe aus:

1. `bash ~/second-brain/automation/brain-auto.sh --status`
2. `python3 ~/second-brain/automation/brain_hygiene.py`
3. `termux-job-scheduler --pending`

Berichte knapp und belegt:

- letzter Automationslauf (Zeit, Modus, Schritte, Health)
- Queue, Eingang, Lektionen, Protokolle, Top-Regeln
- Scheduler-Job 99101 vorhanden?
- Health-Status mit den konkreten Befunden
- eine konkrete nächste Aktion, falls etwas fehlt

Keine Geheimnisse ausgeben, nichts verändern.
