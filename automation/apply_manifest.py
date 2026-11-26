#!/usr/bin/env python3
"""Prüft das Manifest des brain-curator und archiviert Eingangs-Originale.

Vertrauenswürdige, deterministische Schicht: der Agent darf nur Markdown im
Vault schreiben; dieses Skript entscheidet, welche Eingangsdateien tatsächlich
aus 00_Eingang entfernt werden. Es löscht nie, sondern verschiebt nach
70_Archiv/02_Alte_Notizen/.
"""
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path(
    os.environ.get("VAULT")
    or Path.home() / "storage" / "shared" / "SecondBrain"
).resolve()
INGRESS = VAULT / "00_Eingang"
ARCHIVE = VAULT / "70_Archiv" / "02_Alte_Notizen"
ALLOWED_ROOTS = (
    "10_Projekte", "20_Bereiche", "30_Wissen",
    "40_Ressourcen", "50_Personen", "70_Archiv",
)
PROTECTED = {"README.md", "Willkommen.md"}
BASE = Path.home() / "second-brain" / "automation"
LOG_DIR = BASE / "logs"
STATE_DIR = BASE / "state"


def safe_rel(value, root):
    """Nur relative Pfade ohne '..', die innerhalb von root liegen."""
    if not isinstance(value, str) or not value.strip():
        return None
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts or rel.parts[0].startswith("."):
        return None
    target = (root / rel).resolve()
    if target == root or root not in target.parents:
        return None
    return target


def finish(lines, code):
    text = "\n".join(lines) + "\n"
    print(text)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / "apply-latest.log").write_text(text)
    return code


def main():
    manifest_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%F %T")
    lines = [f"=== apply_manifest {stamp} ==="]

    if manifest_path is None or not manifest_path.is_file():
        lines.append("FEHLER: kein Manifest vorhanden - keine Aenderung")
        return finish(lines, 1)

    try:
        raw_text = manifest_path.read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except Exception as exc:
        lines.append(f"FEHLER: Manifest ungueltig: {exc} - keine Aenderung")
        return finish(lines, 1)

    if data.get("dryRun") is True:
        lines.append("TROCKENLAUF - keine Dateien veraendert")
        return finish(lines, 0)

    moves = data.get("moves")
    if not isinstance(moves, list):
        lines.append("FEHLER: moves fehlt oder ist keine Liste - keine Aenderung")
        return finish(lines, 1)

    ok = skipped = 0
    for item in moves:
        if not isinstance(item, dict):
            skipped += 1
            lines.append("SKIP: Eintrag ist kein Objekt")
            continue
        src = safe_rel(item.get("source"), VAULT)
        dst = safe_rel(item.get("destination"), VAULT)
        if src is None or dst is None:
            skipped += 1
            lines.append(f"SKIP: ungueltiger Pfad {item.get('source')} -> {item.get('destination')}")
            continue
        if INGRESS not in src.parents or src.name in PROTECTED:
            skipped += 1
            lines.append(f"SKIP: Quelle nicht im Eingang oder geschuetzt: {src}")
            continue
        if src.suffix.lower() != ".md" or src.is_symlink() or not src.is_file():
            skipped += 1
            lines.append(f"SKIP: Quelle keine normale .md-Datei: {src}")
            continue
        if dst == src or VAULT / "00_Eingang" in dst.parents:
            skipped += 1
            lines.append(f"SKIP: Ziel liegt im Eingang oder ist die Quelle: {dst}")
            continue
        if dst.suffix.lower() != ".md" or dst.is_symlink() or not dst.is_file():
            skipped += 1
            lines.append(f"SKIP: Ziel existiert nicht als normale .md-Datei: {dst}")
            continue
        if dst.stat().st_size == 0:
            skipped += 1
            lines.append(f"SKIP: Zieldatei ist leer: {dst}")
            continue
        if not any(dst.relative_to(VAULT).parts[0] == r for r in ALLOWED_ROOTS):
            skipped += 1
            lines.append(f"SKIP: Ziel ausserhalb erlaubter Ablageordner: {dst}")
            continue

        ARCHIVE.mkdir(parents=True, exist_ok=True)
        target = ARCHIVE / f"verarbeitet-{datetime.now():%F}__{src.name}"
        n = 2
        while target.exists():
            target = ARCHIVE / f"verarbeitet-{datetime.now():%F}__{src.stem}-{n}{src.suffix}"
            n += 1
        try:
            shutil.move(str(src), str(target))
            ok += 1
            lines.append(f"OK: {src.relative_to(VAULT)} -> {dst.relative_to(VAULT)} | Original: {target.name}")
        except Exception as exc:
            skipped += 1
            lines.append(f"SKIP: Verschieben fehlgeschlagen {src}: {exc}")

    # Abdeckungsprüfung: jede noch im Eingang liegende verarbeitbare Notiz
    # muss im Manifest erfasst sein - sonst wurde sie vom Agenten uebersehen.
    remaining = sorted(
        p.name for p in INGRESS.glob("*.md")
        if p.name not in PROTECTED and not p.name.startswith(".")
    )
    unprocessed = [name for name in remaining if name not in raw_text]
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "unprocessed.txt").write_text(
        "\n".join(unprocessed) + ("\n" if unprocessed else "")
    )
    for name in unprocessed:
        lines.append(f"WARN: im Eingang, aber nicht im Manifest erfasst: {name}")

    lines.append(
        f"ERGEBNIS: {ok} archiviert, {skipped} uebersprungen, {len(unprocessed)} unerfasst"
    )
    text = "\n".join(lines) + "\n"
    (LOG_DIR / f"apply-{datetime.now():%F}.log").open("a").write(text)
    try:
        shutil.move(str(manifest_path), str(LOG_DIR / f"manifest-applied-{datetime.now():%Y%m%d-%H%M%S}.json"))
    except Exception as exc:
        lines.append(f"HINWEIS: Manifest konnte nicht archiviert werden: {exc}")
    return finish(lines, 0)


if __name__ == "__main__":
    sys.exit(main())
