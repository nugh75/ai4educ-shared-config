"""sync-global.sh rewrites global files when any generated text changes."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync-global.sh"
TARGETS = (".pi/agent/AGENTS.md", ".claude/CLAUDE.md", ".codex/AGENTS.md", ".opencode/AGENTS.md")


class SyncGlobalTest(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        for target in TARGETS:
            (self.home / target).parent.mkdir(parents=True, exist_ok=True)
        self.env = {**os.environ, "HOME": str(self.home)}

    def run_script(self, *args):
        return subprocess.run(["bash", str(SCRIPT), *args], env=self.env, capture_output=True, text=True)

    def test_stale_generated_text_with_current_hash_is_rewritten_and_reported(self):
        self.run_script()
        claude = self.home / ".claude/CLAUDE.md"
        fresh = claude.read_text()
        self.assertIn("commit-sync.sh", fresh)
        # Stesso hash delle linee guida, ma testo generato vecchio (manca il passo commit-sync).
        stale = "\n".join(line for line in fresh.splitlines() if "commit-sync.sh" not in line) + "\n"
        claude.write_text(stale)
        self.assertIn("Claude Code: stale", self.run_script("--check").stdout)
        self.run_script()
        self.assertEqual(claude.read_text(), fresh)
        # Le skill non esistono nella HOME di prova: si controlla solo la riga del file globale.
        self.assertNotIn("Claude Code: stale", self.run_script("--check").stdout)


if __name__ == "__main__":
    unittest.main()
