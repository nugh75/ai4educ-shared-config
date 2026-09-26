"""commit-sync.sh on real git repositories with bare remotes."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "commit-sync.sh"


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True).stdout.strip()


class CommitSyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.projects = []

    def repo(self, name, remote=True):
        path = self.tmp / name
        subprocess.run(["git", "init", "-q", "-b", "main", str(path)], check=True)
        git(path, "config", "user.email", "t@t")
        git(path, "config", "user.name", "t")
        for f in ("AGENTS.md", "CLAUDE.md", "app.py"):
            (path / f).write_text("old\n")
        git(path, "add", ".")
        git(path, "commit", "-qm", "init")
        if remote:
            bare = self.tmp / f"{name}.git"
            subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
            git(path, "remote", "add", "origin", str(bare))
            git(path, "push", "-q", "-u", "origin", "main")
            git(path, "remote", "set-head", "origin", "main")
        self.projects.append(path)
        return path

    def sync(self, path):
        for f in ("AGENTS.md", "CLAUDE.md"):
            (path / f).write_text("new rules\n")

    def run_script(self, *extra):
        pfile = self.tmp / "projects.txt"
        pfile.write_text("# comment\n" + "\n".join(str(p) for p in self.projects) + "\n")
        return subprocess.run(["bash", str(SCRIPT), "--projects-file", str(pfile), *extra],
                              capture_output=True, text=True)

    def test_commits_and_pushes_only_generated_files_on_default_branch(self):
        repo = self.repo("alpha")
        self.sync(repo)
        (repo / "app.py").write_text("work in progress\n")
        out = self.run_script()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("PUSHED alpha", out.stdout)
        self.assertEqual(git(repo, "log", "-1", "--format=%s"), "chore: sync shared rules")
        self.assertEqual(git(repo, "show", "--name-only", "--format=", "HEAD").split(), ["AGENTS.md", "CLAUDE.md"])
        self.assertEqual(git(repo, "rev-parse", "HEAD"), git(repo, "rev-parse", "origin/main"))
        self.assertIn("app.py", git(repo, "status", "--porcelain"))

    def test_local_only_repository_commits_without_push(self):
        repo = self.repo("local", remote=False)
        self.sync(repo)
        out = self.run_script()
        self.assertIn("LOCAL local", out.stdout)
        self.assertEqual(git(repo, "log", "-1", "--format=%s"), "chore: sync shared rules")

    def test_skips_feature_branch_diverged_staged_and_clean(self):
        feature = self.repo("feature")
        git(feature, "switch", "-qc", "feature/x")
        self.sync(feature)
        diverged = self.repo("diverged")
        (diverged / "app.py").write_text("local\n")
        git(diverged, "commit", "-qam", "local only")
        self.sync(diverged)
        staged = self.repo("staged")
        (staged / "app.py").write_text("staged\n")
        git(staged, "add", "app.py")
        self.sync(staged)
        clean = self.repo("clean")
        heads = {p: git(p, "rev-parse", "HEAD") for p in (feature, diverged, staged, clean)}
        out = self.run_script()
        self.assertIn("SKIP-branch feature", out.stdout)
        self.assertIn("SKIP-diverged diverged", out.stdout)
        self.assertIn("SKIP-staged staged", out.stdout)
        self.assertNotIn("clean", out.stdout.replace("SKIP-clean", ""))
        for p, head in heads.items():
            self.assertEqual(git(p, "rev-parse", "HEAD"), head, p.name)

    def test_fast_forwards_a_repository_that_is_only_behind(self):
        repo = self.repo("behind")
        other = self.tmp / "other"
        subprocess.run(["git", "clone", "-q", str(self.tmp / "behind.git"), str(other)], check=True)
        git(other, "config", "user.email", "t@t")
        git(other, "config", "user.name", "t")
        (other / "README.md").write_text("remote change\n")
        git(other, "add", ".")
        git(other, "commit", "-qm", "remote")
        git(other, "push", "-q")
        self.sync(repo)
        out = self.run_script()
        self.assertIn("PUSHED behind", out.stdout)
        self.assertTrue((repo / "README.md").exists())

    def test_dry_run_changes_nothing(self):
        repo = self.repo("dry")
        self.sync(repo)
        head = git(repo, "rev-parse", "HEAD")
        out = self.run_script("--dry-run")
        self.assertIn("WOULD-PUSH dry", out.stdout)
        self.assertEqual(git(repo, "rev-parse", "HEAD"), head)


if __name__ == "__main__":
    unittest.main()
