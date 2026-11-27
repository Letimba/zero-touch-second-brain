#!/usr/bin/env python3
"""Deterministisches Verifikationsgate für den Lernbereich des Vaults.

Prüft Lektionen, Protokolle und Lernindex ohne LLM. Schreibt
state/learning-verify.json und exit 1 bei kritischen Findings.
"""
import json
import os
import re
from pathlib import Path

HOME = Path.home()
BASE = Path(os.environ.get("SECOND_BRAIN_HOME", str(HOME / "second-brain"))) / "automation"
VAULT = Path(os.environ.get("VAULT", str(HOME / "SecondBrain")))
MEM = VAULT / "95_System/Agentenverwaltung/04_Gedaechtnis_und_Kontext"
LESSONS = MEM / "Lektionen"
PROTOCOLS = MEM / "Lernprotokolle"
INDEX = MEM / "_Lernindex.md"
OUT = BASE / "state/learning-verify.json"

SECRET = re.compile(
    r"0t[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"(?i:password|passwd|token|secret|api[_-]?key)\s*[:=]\s*\S{6,}"
)
PERSONAL = re.compile(r"/data/data/com\.termux|/storage/[a-z]+/0|Letimba")
REQUIRED = ("typ", "status", "erstellt", "prioritaet", "bestaetigt_am")


def frontmatter(text):
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    out = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def main():
    findings = []
    lessons = sorted(LESSONS.glob("L-*.md")) if LESSONS.is_dir() else []
    protocols = sorted(
        p for p in PROTOCOLS.glob("*.md") if p.name != "README.md"
    ) if PROTOCOLS.is_dir() else []

    if not lessons:
        findings.append("critical: keine Lektionen gefunden")
    for p in lessons:
        t = p.read_text(encoding="utf-8", errors="ignore")
        fm = frontmatter(t)
        for key in REQUIRED:
            if key not in fm:
                findings.append(f"critical: {p.name} fehlt {key}")
        words = len(t.split())
        if words >= 400:
            findings.append(f"critical: {p.name} hat {words} Wörter (>=400)")
        if t.count("[[") < 2:
            findings.append(f"warning: {p.name} hat <2 Wikilinks")
        if SECRET.search(t) or PERSONAL.search(t):
            findings.append(f"critical: {p.name} enthält Secret/PII-Muster")

    for p in protocols:
        t = p.read_text(encoding="utf-8", errors="ignore")
        if len(t.split()) > 300:
            findings.append(f"warning: {p.name} >300 Wörter")
        if SECRET.search(t) or PERSONAL.search(t):
            findings.append(f"critical: {p.name} enthält Secret/PII-Muster")

    if not INDEX.is_file():
        findings.append("critical: _Lernindex.md fehlt")
    else:
        idx = INDEX.read_text(encoding="utf-8", errors="ignore")
        rules = [line for line in idx.splitlines() if re.match(r"^\|\s*P[0-3]\s*\|", line)]
        if len(rules) > 10:
            findings.append("critical: >10 Top-Regeln im Lernindex")
        known = {p.stem for p in lessons}
        for name in re.findall(r"\[\[([^\]|]+)", idx):
            stem = name.split("/")[-1]
            if stem.startswith("L-") and stem not in known:
                findings.append(f"warning: Index verweist auf fehlende Lektion {stem}")

    critical = sum(1 for f in findings if f.startswith("critical"))
    result = {
        "status": "ok" if not critical else "critical",
        "critical": critical,
        "warnings": sum(1 for f in findings if f.startswith("warning")),
        "lessons": len(lessons),
        "protocols": len(protocols),
        "top_rules": len(rules) if INDEX.is_file() else 0,
        "findings": findings,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(OUT)
    print(json.dumps({k: v for k, v in result.items() if k != "findings"}, ensure_ascii=False))
    for f in findings:
        print(f)
    return 1 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
