import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRET = re.compile(r"0t[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}")
PERSONAL = re.compile(r"/storage/emulated|/data/data/com\.termux|tim-engine|Völker")
SKIP = {"verify.sh", "test_release.py", "RELEASE-CHECKLIST.md", "DISTRIBUTION-PLAN.md", "brain-auto-termux.sh"}


class ReleaseTest(unittest.TestCase):
    def test_required_files(self):
        for name in ("LICENSE", "README.md", "QUICKSTART.md", "SECURITY.md",
                     "CONTRIBUTING.md", "CHANGELOG.md", ".gitignore"):
            self.assertTrue((ROOT / name).is_file(), name)

    def test_no_secrets_or_personal_paths(self):
        for path in ROOT.rglob("*"):
            if (not path.is_file() or ".git" in path.parts
                    or "__pycache__" in path.parts or path.suffix == ".pyc"
                    or path.name in SKIP):
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            self.assertIsNone(SECRET.search(text), f"secret-shaped value in {path}")
            self.assertIsNone(PERSONAL.search(text), f"personal path in {path}")

    def test_example_vault_is_synthetic(self):
        vault = ROOT / "examples" / "vault"
        for name in ("50_Personen", "60_Tagebuch"):
            self.assertFalse((vault / name).exists(), name)
        raw = vault / "00_Rohdaten"
        if raw.exists():
            self.assertEqual([p.name for p in raw.iterdir() if p.is_file()], ["README.md"])

    def test_no_runtime_data(self):
        for name in ("automation/logs", "automation/state", "automation/queue"):
            self.assertFalse((ROOT / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
