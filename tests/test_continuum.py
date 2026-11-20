"""Run: python -m unittest discover -s tests -v"""
import tempfile
import unittest
from pathlib import Path

from continuum import connect, scan, stats


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root = base / "documents"
        self.root.mkdir()
        self.db = base / "registry.sqlite3"
        self.conn = connect(self.db)
        self.addCleanup(self.conn.close)

    def inventory(self):
        return scan(self.conn, str(self.root), str(self.db))

    def row(self, name):
        return self.conn.execute("SELECT * FROM locations WHERE path=?",
                                 (str(self.root / name),)).fetchone()

    def test_discovery_and_repeat_are_stable(self):
        (self.root / "a.md").write_text("hello", encoding="utf-8")
        self.assertEqual(self.inventory()["status"], "complete")
        first = self.row("a.md")["asset_id"]
        self.inventory()
        self.assertEqual(self.row("a.md")["asset_id"], first)
        self.assertEqual(stats(self.conn)["assets"], 1)
        self.assertEqual(stats(self.conn)["versions"], 1)

    def test_edit_adds_version_without_changing_identity(self):
        p = self.root / "a.md"
        p.write_text("original")
        self.inventory()
        aid = self.row("a.md")["asset_id"]
        p.write_text("updated with additional words")
        self.inventory()
        self.assertEqual(self.row("a.md")["asset_id"], aid)
        self.assertEqual(stats(self.conn)["versions"], 2)
        kinds = [r[0] for r in self.conn.execute(
            "SELECT kind FROM events WHERE asset_id=?", (aid,))]
        self.assertIn("content_changed", kinds)

    def test_rename_tracks_identity(self):
        (self.root / "old.txt").write_text("unchanged")
        self.inventory()
        aid = self.row("old.txt")["asset_id"]
        (self.root / "old.txt").rename(self.root / "new.txt")
        self.inventory()
        self.assertEqual(self.row("new.txt")["asset_id"], aid)
        self.assertIsNone(self.row("old.txt"))
        self.assertIn("path_changed", [r[0] for r in self.conn.execute(
            "SELECT kind FROM events WHERE asset_id=?", (aid,))])

    def test_identical_copy_has_separate_identity(self):
        (self.root / "one.txt").write_text("identical bytes")
        (self.root / "two.txt").write_text("identical bytes")
        self.inventory()
        one, two = self.row("one.txt"), self.row("two.txt")
        self.assertEqual(one["hash"], two["hash"])
        self.assertNotEqual(one["asset_id"], two["asset_id"])

    def test_disappearance_preserves_history(self):
        p = self.root / "old.txt"
        p.write_text("hi")
        self.inventory()
        aid = self.row("old.txt")["asset_id"]
        p.unlink()
        self.inventory()
        self.assertEqual(self.row("old.txt")["state"], "not_observed")
        self.assertEqual(self.row("old.txt")["asset_id"], aid)

    def test_symlink_directory_is_not_traversed(self):
        ext = Path(self.temp.name) / "outside"
        ext.mkdir()
        (ext / "private.txt").write_text("not indexed")
        try:
            (self.root / "link").symlink_to(ext, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not permitted on this platform")
        result = self.inventory()
        self.assertEqual(result["status"], "partial")
        self.assertEqual(stats(self.conn)["assets"], 0)

    def test_db_inside_root_is_rejected(self):
        inside = self.root / "index.sqlite3"
        with self.assertRaises(ValueError):
            scan(self.conn, str(self.root), str(inside))


if __name__ == "__main__":
    unittest.main()
