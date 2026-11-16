import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import types
import unittest


PROJECT = Path(__file__).resolve().parents[1]
PLUGIN = PROJECT / "hermes" / "plugins" / "channel-knowledge"


def load(name):
    package = sys.modules.setdefault("shoh_plugin", types.ModuleType("shoh_plugin"))
    package.__path__ = [str(PLUGIN)]
    spec = importlib.util.spec_from_file_location(f"shoh_plugin.{name}", PLUGIN / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


onboarding = load("onboarding")
retrieval = load("retrieval")


class OnboardingTests(unittest.TestCase):
    def test_saved_owner_fact_is_searchable_and_history_kept(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "audience.md").write_text("---\nstatus: pending-evidence\nupdated: 2026-11-14\n---\n\n# Audience\n",
                                              encoding="utf-8")
            result = onboarding.save_knowledge(str(root), "audience.md", "Daraja",
                                               "Most learners target band 6.5 to 7.0, aged 17-24.")
            self.assertEqual(result["status"], "saved")
            text = (root / "audience.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\nstatus: active\n"))
            self.assertEqual(text.count("status:"), 1)
            self.assertEqual(len(list((root / ".history").iterdir())), 1)
            hit = retrieval.search(root, root / "i.db", "learners band 6.5")
            self.assertEqual(hit["sources"][0]["file"], "knowledge/audience.md")
            self.assertIn("6.5", hit["sources"][0]["excerpt"])

    def test_write_scope_is_enforced(self):
        with TemporaryDirectory() as tmp:
            for file in ("shoh-workflows.md", "../evil.md", "README.md"):
                with self.assertRaises(ValueError):
                    onboarding.save_knowledge(tmp, file, "X section", "some text here")
            with self.assertRaises(ValueError):
                onboarding.save_knowledge(tmp, "decisions.md", "two\nlines", "some text here")
            self.assertEqual(onboarding.save_knowledge("relative/dir", "decisions.md", "Sec", "some text")["status"],
                             "unavailable")
            # A fake frontmatter delimiter in owner text must not end up in the file body.
            onboarding.save_knowledge(tmp, "decisions.md", "Narx", "line one\n---\nstatus: active")
            body = (Path(tmp) / "decisions.md").read_text(encoding="utf-8")
            self.assertEqual(body.count("\n---\n"), 1)

    def test_onboarding_progress_and_completion(self):
        with TemporaryDirectory() as tmp:
            profile = Path(tmp)
            first = onboarding.status(profile, None)
            self.assertFalse(first["onboarding_complete"])
            self.assertEqual(first["onboarding_pending"][0]["key"], "teacher")
            saved = onboarding.record(profile, "teacher", "Ustoz Shoxrux, IELTSSHOKH")
            self.assertNotIn("teacher", saved["remaining"])
            with self.assertRaises(ValueError):
                onboarding.record(profile, "api_key", "x")
            onboarding.record(profile, "complete", None)
            state = json.loads((profile / onboarding.STATE_FILE).read_text(encoding="utf-8"))
            self.assertIn("completed_at", state)
            self.assertTrue(onboarding.status(profile, None)["onboarding_complete"])


if __name__ == "__main__":
    unittest.main()
