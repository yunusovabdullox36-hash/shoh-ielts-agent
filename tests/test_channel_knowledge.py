import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


PROJECT = Path(__file__).resolve().parents[1]
MODULE = PROJECT / "hermes" / "plugins" / "channel-knowledge" / "retrieval.py"
SPEC = importlib.util.spec_from_file_location("channel_retrieval", MODULE)
retrieval = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(retrieval)


class ChannelKnowledgeTests(unittest.TestCase):
    def test_policy_search_returns_source_and_lines(self):
        with TemporaryDirectory() as tmp:
            result = retrieval.search(PROJECT / "knowledge", Path(tmp) / "index.db",
                                      "nashr uchun tasdiq kerakmi?")
        self.assertEqual(result["status"], "matched")
        first = result["sources"][0]
        self.assertEqual(first["file"], "knowledge/decisions.md")
        self.assertIn("exact draft revision", first["excerpt"])
        self.assertGreater(first["lines"][0], 4)

    def test_uzbek_inflected_queries_reach_their_section(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "index.db"
            (root / "channel-profile.md").write_text(
                "---\nstatus: active\n---\n# Intro\nOwner text.\n\n## Channels\n"
                "| Channel | Subscribers |\n| @demo | 3760 obunachilar |\n", encoding="utf-8")
            (root / "brand-voice.md").write_text(
                "---\nstatus: active\n---\n# Brand\nSource line.\n\n## Visual\nPalette rang: navy, gold.\n",
                encoding="utf-8")
            for query, file, needle in (("kanalda nechta obunachi bor", "channel-profile.md", "3760"),
                                        ("brend ranglari qanday", "brand-voice.md", "navy")):
                result = retrieval.search(root, db, query)
                self.assertEqual(result["status"], "matched", query)
                self.assertEqual(result["sources"][0]["file"], f"knowledge/{file}", query)
                self.assertIn(needle, result["sources"][0]["excerpt"], query)
        self.assertEqual(retrieval.stem("ranglari"), "rang")
        self.assertEqual(retrieval.stem("kanalda"), "kanal")
        self.assertEqual(retrieval.stem("ona"), "ona")

    def test_unapproved_and_removed_sources_do_not_leak(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "index.db"
            source = root / "audience.md"
            source.write_text("---\nstatus: approved\n---\n# Audience\nRaremetric 42", encoding="utf-8")
            self.assertEqual(retrieval.search(root, db, "raremetric")["status"], "matched")
            source.write_text("---\nstatus: pending-evidence\n---\nRaremetric 42", encoding="utf-8")
            (root / "private.md").write_text("---\nstatus: approved\n---\nRaremetric secret", encoding="utf-8")
            self.assertEqual(retrieval.search(root, db, "raremetric")["status"], "no_match")

    def test_query_does_not_allow_fts_operators_or_unbounded_output(self):
        with TemporaryDirectory() as tmp:
            db = Path(tmp) / "index.db"
            self.assertEqual(retrieval.search(PROJECT / "knowledge", db, '* OR "xyzzq"')["status"],
                             "no_match")
            with self.assertRaises(ValueError):
                retrieval.search(PROJECT / "knowledge", db, "approval", 100)
