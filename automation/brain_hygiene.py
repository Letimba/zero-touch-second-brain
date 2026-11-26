#!/usr/bin/env python3
"""Health check for the Second Brain learning loop and automation.

Runs the read-only vault lint, checks inbox/queue/lesson/index consistency,
scans the learning area for secrets, and writes:

- state/health.json                     machine-readable status
- <vault>/95_System/Agentenverwaltung/02_Aufgaben/_brain-health.md

Exit codes: 0 = ok/warn, 1 = fail (critical findings or secrets).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

HOME = Path.home()
BASE = HOME / "second-brain/automation"
VAULT = Path(os.environ.get("VAULT", str(HOME / "SecondBrain")))
MEM = VAULT / "95_System/Agentenverwaltung/04_Gedaechtnis_und_Kontext"
LESSONS = MEM / "Lektionen"
PROTOCOLS = MEM / "Lernprotokolle"
INDEX = MEM / "_Lernindex.md"
INBOX = VAULT / "00_Eingang"
QUEUE = BASE / "queue"
STATE = BASE / "state"
REPORT = VAULT / "95_System/Agentenverwaltung/02_Aufgaben/_brain-health.md"
OPENCODE_JSON = HOME / ".config/opencode/opencode.json"
COMMAND = HOME / ".config/opencode/commands/session-learn.md"

sys.path.insert(0, str(BASE))
try:
    from session_export import STRONG_SECRET  # type: ignore
except Exception:  # pragma: no cover - defensive
    STRONG_SECRET = re.compile(
        r"(0t[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|"
        r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
    )

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
TOP_TABLE_ROW = re.compile(r"^\|\s*P[0-2]\s*\|", re.M)


def iso_today() -> str:
    return date.today().isoformat()


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))


def note_files(folder: Path, pattern: str = "*.md") -> list[Path]:
    if not folder.exists():
        return []
    return sorted(
        p
        for p in folder.glob(pattern)
        if p.is_file() and not p.name.startswith(".")
    )


def inbox_notes() -> list[Path]:
    skip = {"README.md", "Willkommen.md"}
    return [p for p in note_files(INBOX) if p.name not in skip]


def queue_notes() -> list[Path]:
    return note_files(QUEUE)


def check_vault_lint() -> dict:
    lint = VAULT / "95_System/vault-lint.py"
    if not lint.exists():
        return {"ok": False, "result": "missing", "critical": -1, "output": ""}
    try:
        proc = subprocess.run(
            [sys.executable, str(lint)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(VAULT),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "result": "error", "critical": -1, "output": str(exc)}
    output = (proc.stdout or "") + (proc.stderr or "")
    match = re.search(r"RESULT:\s*(OK|FAIL)\s*\((\d+) critical", output)
    result = match.group(1) if match else "unknown"
    critical = int(match.group(2)) if match else -1
    return {
        "ok": proc.returncode == 0 and result == "OK",
        "result": result,
        "critical": critical,
        "output": output,
    }


def check_learning() -> dict:
    lessons = note_files(LESSONS, "L-*.md")
    protocols = note_files(PROTOCOLS, "*.md")
    protocols = [p for p in protocols if p.name != "README.md"]
    index_text = read(INDEX)
    index_links = {
        target.split("|", 1)[0].strip().rsplit("/", 1)[-1]
        for target in WIKILINK.findall(index_text)
        if target.split("|", 1)[0].strip().rsplit("/", 1)[-1].startswith("L-")
    }
    on_disk = {p.stem for p in lessons}
    missing_in_index = sorted(on_disk - index_links)
    missing_on_disk = sorted(index_links - on_disk)
    top_rules = len(TOP_TABLE_ROW.findall(index_text))

    stale: list[str] = []
    oversized_lessons: list[str] = []
    short_lessons: list[str] = []
    broken_lesson_fm: list[str] = []
    stale_cutoff = date.today() - timedelta(days=90)

    for lesson in lessons:
        text = read(lesson)
        fm = frontmatter(text)
        for key in ("typ", "status", "erstellt", "aktualisiert"):
            if not fm.get(key):
                broken_lesson_fm.append(f"{lesson.name}:{key}")
        if fm.get("typ") != "lektion":
            broken_lesson_fm.append(f"{lesson.name}:typ")
        dates = [date.fromisoformat(d) for d in DATE.findall(fm.get("bestaetigt_am", "")) if d]
        if not dates:
            dates = [date.fromisoformat(d) for d in DATE.findall(fm.get("erstellt", "")) if d]
        if dates and max(dates) < stale_cutoff:
            stale.append(lesson.name)
        if word_count(text) > 400:
            oversized_lessons.append(lesson.name)
        links = [t for t in WIKILINK.findall(text) if t.split("|", 1)[0].strip()]
        if len(links) < 2:
            short_lessons.append(lesson.name)

    oversized_protocols = [
        p.name for p in protocols if word_count(read(p)) > 300
    ]

    return {
        "lessons": len(lessons),
        "protocols": len(protocols),
        "top_rules": top_rules,
        "index_links": len(index_links),
        "missing_in_index": missing_in_index,
        "missing_on_disk": missing_on_disk,
        "stale": stale,
        "oversized_lessons": oversized_lessons,
        "lessons_with_few_links": short_lessons,
        "broken_lesson_frontmatter": broken_lesson_fm,
        "oversized_protocols": oversized_protocols,
    }


def check_secrets() -> list[str]:
    hits: list[str] = []
    folders = [QUEUE, LESSONS, PROTOCOLS, INBOX]
    for folder in folders:
        for path in note_files(folder):
            text = read(path)
            if STRONG_SECRET.search(text):
                hits.append(str(path.relative_to(VAULT)) if path.is_relative_to(VAULT) else str(path))
    for path in (INDEX,):
        if STRONG_SECRET.search(read(path)):
            hits.append(str(path.relative_to(VAULT)))
    return sorted(set(hits))


def check_registration() -> dict:
    agent_ok = False
    json_ok = False
    try:
        data = json.loads(read(OPENCODE_JSON))
        json_ok = True
        agent_ok = "brain-scribe" in (data.get("agent") or {})
    except (ValueError, OSError):
        pass
    return {
        "opencode_json_valid": json_ok,
        "brain_scribe_registered": agent_ok,
        "session_learn_command": COMMAND.exists(),
    }


def check_scheduler() -> dict:
    try:
        proc = subprocess.run(
            ["termux-job-scheduler", "--pending"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "job_99101": False, "output": str(exc)}
    return {
        "available": True,
        "job_99101": "99101" in output,
        "output": output.strip(),
    }


def build_report(health: dict) -> str:
    status = health["status"]
    icon = {"ok": "✅ OK", "warn": "⚠️ Warnung", "fail": "❌ Fehler"}[status]
    learning = health["learning"]
    lint = health["vault_lint"]
    scheduler = health["scheduler"]
    registration = health["registration"]

    findings: list[str] = []
    if lint.get("critical", -1) > 0:
        findings.append(f"Vault-Lint: {lint['critical']} kritische Befunde.")
    if health["secrets"]:
        findings.append(f"Geheimnis-Muster in {len(health['secrets'])} Datei(en): " + ", ".join(health["secrets"][:5]))
    if learning["missing_in_index"]:
        findings.append("Lektionen fehlen im Lernindex: " + ", ".join(learning["missing_in_index"][:5]))
    if learning["missing_on_disk"]:
        findings.append("Lernindex verlinkt fehlende Lektionen: " + ", ".join(learning["missing_on_disk"][:5]))
    if learning["top_rules"] > 10:
        findings.append(f"Top-Regeln überschreiten das Limit: {learning['top_rules']} statt max. 10.")
    if learning["stale"]:
        findings.append("Seit 90 Tagen nicht bestätigt: " + ", ".join(learning["stale"][:5]))
    if learning["oversized_lessons"]:
        findings.append("Lektionen über 400 Wörter: " + ", ".join(learning["oversized_lessons"][:5]))
    if learning["broken_lesson_frontmatter"]:
        findings.append("Frontmatter-Probleme: " + ", ".join(learning["broken_lesson_frontmatter"][:5]))
    if not registration["brain_scribe_registered"]:
        findings.append("Agent `brain-scribe` ist nicht in opencode.json registriert.")
    if not scheduler["job_99101"]:
        findings.append("Scheduler-Job 99101 ist nicht registriert.")
    if health["inbox_count"] > 0:
        findings.append(f"Eingang enthält {health['inbox_count']} unverarbeitete Notiz(en).")
    if health["queue_count"] > 3:
        findings.append(f"Lern-Queue hat {health['queue_count']} offene Digests (Rückstau).")

    if not findings:
        findings.append("Keine Befunde.")

    lines = [
        "---",
        "typ: hub",
        "status: aktiv",
        f"aktualisiert: {health['generated']}",
        "tags: [system, health, automation, second-brain]",
        "---",
        "# Brain-Health",
        "",
        f"**Status:** {icon}  ",
        f"**Erzeugt:** {health['generated']}  ",
        f"**Nächster Lauf:** automatisch über `brain-auto.sh` (Scheduler 99101, alle 15 Minuten)",
        "",
        "## Kennzahlen",
        "",
        "| Prüfung | Wert |",
        "|---|---|",
        f"| Vault-Lint | {lint.get('result', '?')} ({lint.get('critical', '?')} kritisch) |",
        f"| Notizen gesamt | {health['notes_total']} |",
        f"| Lektionen | {learning['lessons']} |",
        f"| Protokolle | {learning['protocols']} |",
        f"| Top-Regeln | {learning['top_rules']} / 10 |",
        f"| Eingang | {health['inbox_count']} |",
        f"| Lern-Queue | {health['queue_count']} |",
        f"| Scheduler 99101 | {'registriert' if scheduler['job_99101'] else 'fehlt'} |",
        f"| brain-scribe | {'registriert' if registration['brain_scribe_registered'] else 'fehlt'} |",
        "",
        "## Befunde",
        "",
    ]
    lines.extend(f"- {item}" for item in findings)
    lines += [
        "",
        "## Nächste Aktionen",
        "",
        "- Bei Rückstau: `brain-auto.sh --session-now` ausführen.",
        "- Bei fehlenden Lektionen im Index: `brain-scribe` erneut laufen lassen.",
        "- Bei Geheimnis-Funden: Datei prüfen, Inhalt entfernen, Vorfall im Protokoll vermerken.",
        "",
        "## Technik",
        "",
        "- Erzeugt von `~/second-brain/automation/brain_hygiene.py`.",
        "- Maschinenlesbar: `~/second-brain/automation/state/health.json`.",
        "- Diese Seite wird bei jedem Lauf überschrieben; keine manuellen Ergänzungen.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    STATE.mkdir(parents=True, exist_ok=True)
    lint = check_vault_lint()
    learning = check_learning()
    secrets = check_secrets()
    registration = check_registration()
    scheduler = check_scheduler()

    notes_total = 0
    if lint.get("output"):
        match = re.search(r"notes total\s*:\s*(\d+)", lint["output"])
        if match:
            notes_total = int(match.group(1))

    critical = lint.get("critical", -1)
    warnings = sum(
        [
            len(learning["missing_in_index"]),
            len(learning["missing_on_disk"]),
            len(learning["stale"]),
            len(learning["oversized_lessons"]),
            len(learning["broken_lesson_frontmatter"]),
            max(0, learning["top_rules"] - 10),
            len(secrets),
            0 if registration["brain_scribe_registered"] else 1,
            0 if registration["opencode_json_valid"] else 1,
            0 if scheduler["job_99101"] else 1,
        ]
    )

    if critical > 0 or secrets or not registration["opencode_json_valid"]:
        status = "fail"
    elif warnings > 0:
        status = "warn"
    else:
        status = "ok"

    health = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": status,
        "vault_lint": lint,
        "notes_total": notes_total,
        "inbox_count": len(inbox_notes()),
        "queue_count": len(queue_notes()),
        "learning": learning,
        "secrets": secrets,
        "registration": registration,
        "scheduler": scheduler,
    }

    tmp = STATE / "health.json.tmp"
    tmp.write_text(json.dumps(health, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STATE / "health.json")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(build_report(health), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": status,
                "critical": critical,
                "warnings": warnings,
                "inbox": health["inbox_count"],
                "queue": health["queue_count"],
                "lessons": learning["lessons"],
                "protocols": learning["protocols"],
                "top_rules": learning["top_rules"],
                "secrets": len(secrets),
                "scheduler": scheduler["job_99101"],
                "report": str(REPORT),
            },
            ensure_ascii=False,
        )
    )
    return 1 if status == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
