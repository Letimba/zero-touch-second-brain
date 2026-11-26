#!/usr/bin/env python3
"""Export recent OpenCode sessions to redacted digests for brain-scribe.

Reads the running OpenCode server coordinates from
~/.local/state/opencode/service.json, fetches sessions and messages through the
v2 HTTP API, extracts only user/assistant text, redacts secrets, and writes one
markdown digest per changed session into the automation queue.

Exit codes: 0 = ok (including "nothing to do"), 1 = hard error (server/API).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HOME = Path.home()
SERVICE_FILE = HOME / ".local/state/opencode/service.json"
BASE = HOME / "second-brain/automation"
QUEUE = BASE / "queue"
STATE_DIR = BASE / "state"
LOGS = BASE / "logs"
STATE_FILE = STATE_DIR / "sessions.json"

SKIP_AGENTS = {"brain-curator", "brain-scribe"}

SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|"
            r"private[_-]?key|client[_-]?secret)\s*[:=]\s*[\"']?([^\s\"',;]{6,})"
        ),
        r"\1=[REDACTED]",
    ),
    (re.compile(r"\b0t[A-Za-z0-9_-]{20,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "[REDACTED_KEY]"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_KEY]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._-]{20,}\b"), "Bearer [REDACTED]"),
    (
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            re.S,
        ),
        "[REDACTED_PRIVATE_KEY]",
    ),
    (re.compile(r"(?i)(https?://)[^/\s:@]+:[^/\s@]+@"), r"\1[REDACTED]@"),
]

STRONG_SECRET = re.compile(
    r"(0t[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"(?i:password|passwd|token|secret|api[_-]?key)\s*[:=]\s*\S{6,})"
)


def now_ms() -> int:
    return int(time.time() * 1000)


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def redact(text: str) -> str:
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def load_state() -> dict:
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    tmp.replace(STATE_FILE)


def service_coordinates() -> tuple[str, str]:
    data = json.loads(SERVICE_FILE.read_text(encoding="utf-8"))
    url = str(data["url"]).rstrip("/")
    password = str(data["password"])
    return url, password


def api_get(path: str, timeout: int = 30):
    url, password = service_coordinates()
    token = base64.b64encode(f"opencode:{password}".encode()).decode()
    request = Request(
        url + path,
        headers={
            "Authorization": f"Basic {token}",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", "replace")
    return json.loads(body)


def message_text(message: dict) -> str:
    kind = message.get("type")
    if kind == "user":
        return str(message.get("text") or "").strip()
    if kind == "assistant":
        chunks: list[str] = []
        for part in message.get("content") or []:
            if isinstance(part, dict) and part.get("type") == "text":
                text = str(part.get("text") or "").strip()
                if text:
                    chunks.append(text)
        return "\n".join(chunks).strip()
    return ""


def build_transcript(messages: list[dict], max_chars: int = 90000, per_msg: int = 8000) -> str:
    blocks: list[str] = []
    for message in messages:
        text = message_text(message)
        if not text:
            continue
        if len(text) > per_msg:
            text = text[:per_msg] + "\n[… gekürzt …]"
        role = "User" if message.get("type") == "user" else "Assistant"
        blocks.append(f"### {role}\n{text}")

    if not blocks:
        return ""

    total = sum(len(block) + 2 for block in blocks)
    if total > max_chars:
        head = blocks[:3]
        budget = max_chars - sum(len(block) + 2 for block in head) - 2000
        tail: list[str] = []
        for block in reversed(blocks[3:]):
            if budget - (len(block) + 2) < 0:
                break
            tail.append(block)
            budget -= len(block) + 2
        blocks = head + ["[… Mitte gekürzt …]"] + list(reversed(tail))

    return "\n\n".join(blocks)


def build_digest(session: dict, messages: list[dict], transcript: str) -> str:
    sid = str(session.get("id") or "unknown")
    title = str(session.get("title") or "(ohne Titel)")
    agent = str(session.get("agent") or "?")
    times = session.get("time") or {}
    updated = int(times.get("updated") or now_ms())
    stamp = datetime.fromtimestamp(updated / 1000, tz=timezone.utc).astimezone()
    return (
        "---\n"
        f"session_id: {sid}\n"
        f"titel: {json.dumps(title, ensure_ascii=False)}\n"
        f"agent: {agent}\n"
        f"exportiert: {iso_now()}\n"
        f"session_aktualisiert: {stamp.strftime('%Y-%m-%d %H:%M')}\n"
        f"nachrichten: {len(messages)}\n"
        "---\n\n"
        f"# Session-Digest: {title}\n\n"
        "> Automatisch exportiert aus OpenCode. Nur User- und Assistant-Text, "
        "keine Tool-Ausgaben, keine Reasoning-Daten. Geheimnisse wurden redigiert.\n\n"
        "## Verlauf\n\n"
        f"{transcript}\n"
    )


def select_sessions(
    sessions: list[dict],
    state: dict,
    days: int,
    idle_min: int,
    limit: int,
    latest: bool,
    all_sessions: bool,
) -> list[dict]:
    now = now_ms()
    eligible: list[dict] = []
    for session in sessions:
        sid = str(session.get("id") or "")
        if not sid:
            continue
        agent = str(session.get("agent") or "")
        if agent in SKIP_AGENTS:
            continue
        updated = int((session.get("time") or {}).get("updated") or 0)
        if updated <= 0:
            continue
        if not latest:
            if now - updated > days * 86400 * 1000:
                continue
            if now - updated < idle_min * 60 * 1000:
                continue
        eligible.append(session)

    eligible.sort(key=lambda s: int((s.get("time") or {}).get("updated") or 0))

    if latest:
        return eligible[-1:]

    if all_sessions:
        return eligible[:limit]

    changed = [
        session
        for session in eligible
        if int((session.get("time") or {}).get("updated") or 0)
        != int((state.get(str(session.get("id")), {}) or {}).get("updated") or 0)
    ]
    return changed[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7, help="lookback window in days")
    parser.add_argument("--idle-min", type=int, default=10, help="minimum idle minutes")
    parser.add_argument("--limit", type=int, default=3, help="max sessions per run")
    parser.add_argument("--latest", action="store_true", help="force the latest session")
    parser.add_argument("--all", action="store_true", help="ignore the state file")
    parser.add_argument("--session", help="export one specific session id")
    parser.add_argument("--list", action="store_true", help="list candidates and exit")
    args = parser.parse_args()

    QUEUE.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    if not SERVICE_FILE.exists():
        print(json.dumps({"error": "service.json missing"}))
        return 1

    try:
        payload = api_get("/api/session")
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError) as exc:
        print(json.dumps({"error": f"api unavailable: {exc.__class__.__name__}"}))
        return 1

    sessions = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(sessions, list):
        print(json.dumps({"error": "unexpected /api/session payload"}))
        return 1

    state = load_state()

    if args.session:
        chosen = [s for s in sessions if str(s.get("id")) == args.session]
        if not chosen:
            print(json.dumps({"error": "session not found", "session": args.session}))
            return 1
    else:
        chosen = select_sessions(
            sessions,
            state,
            days=args.days,
            idle_min=args.idle_min,
            limit=args.limit,
            latest=args.latest,
            all_sessions=args.all,
        )

    if args.list:
        print(
            json.dumps(
                {
                    "candidates": [
                        {
                            "id": s.get("id"),
                            "title": s.get("title"),
                            "agent": s.get("agent"),
                            "updated": (s.get("time") or {}).get("updated"),
                        }
                        for s in chosen
                    ]
                },
                ensure_ascii=False,
            )
        )
        return 0

    exported: list[dict] = []
    skipped: list[dict] = []

    for session in chosen:
        sid = str(session.get("id"))
        try:
            messages_payload = api_get(f"/api/session/{sid}/message", timeout=45)
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            skipped.append({"id": sid, "reason": f"messages: {exc.__class__.__name__}"})
            continue

        messages = messages_payload.get("data") if isinstance(messages_payload, dict) else messages_payload
        if not isinstance(messages, list):
            skipped.append({"id": sid, "reason": "unexpected message payload"})
            continue

        transcript = build_transcript(messages)
        if not transcript:
            skipped.append({"id": sid, "reason": "no user/assistant text"})
            continue

        transcript = redact(transcript)
        digest = build_digest(session, messages, transcript)
        digest_hash = hashlib.sha256(digest.encode("utf-8")).hexdigest()
        queue_file = QUEUE / f"{sid}.md"
        previous = state.get(sid, {}) or {}
        if queue_file.exists() and previous.get("hash") == digest_hash:
            skipped.append({"id": sid, "reason": "unchanged"})
            continue

        tmp = queue_file.with_suffix(".tmp")
        tmp.write_text(digest, encoding="utf-8")
        tmp.replace(queue_file)

        state[sid] = {
            **previous,
            "updated": int((session.get("time") or {}).get("updated") or 0),
            "hash": digest_hash,
            "exported_at": iso_now(),
            "title": session.get("title"),
            "agent": session.get("agent"),
            "queue": str(queue_file),
        }
        exported.append(
            {
                "id": sid,
                "title": session.get("title"),
                "agent": session.get("agent"),
                "chars": len(transcript),
                "queue": str(queue_file),
            }
        )

    save_state(state)
    print(json.dumps({"exported": exported, "skipped": skipped}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
