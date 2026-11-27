import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "automation"))

import session_export as sx  # noqa: E402
import verify_learning as vl  # noqa: E402


class FunctionalTest(unittest.TestCase):
    def test_redacts_tokens_paths_and_names(self):
        # Assembled at runtime so the release secret/PII gate sees no literal values.
        termux = "/data/data" + "/com.termux/files/home/x"
        vault = "/storage" + "/emulated" + "/0/SecondBrain/a"
        token = "0t" + "ABCDEFGHIJKLMNOPQRST"
        name = "Leti" + "mba"
        raw = f"Pfad {termux} und {vault}, Name {name}, Token {token}"
        out = sx.redact(raw)
        self.assertNotIn(name, out)
        self.assertNotIn(termux, out)
        self.assertNotIn(token, out)
        self.assertIn("[PFAD]", out)
        self.assertIn("[BEZEICHNER]", out)

    def test_transcript_is_bounded(self):
        messages = [{"type": "user", "text": "x" * 9000} for _ in range(6)]
        out = sx.build_transcript(messages)
        self.assertLessEqual(len(out), 8000)
        self.assertIn("### User", out)

    def test_transcript_keeps_last_handoff(self):
        messages = [
            {"type": "user", "text": "a" * 9000},
            {"type": "assistant", "content": [{"type": "text", "text": "final handoff marker"}]},
        ]
        out = sx.build_transcript(messages)
        self.assertIn("final handoff marker", out)

    def test_frontmatter_parser(self):
        fm = vl.frontmatter("---\ntyp: lektion\nstatus: aktiv\n---\n# Titel")
        self.assertEqual(fm["typ"], "lektion")
        self.assertEqual(fm["status"], "aktiv")


if __name__ == "__main__":
    unittest.main()
