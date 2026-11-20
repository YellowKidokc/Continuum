"""Continuum M1: read-only file inventory, stable observations and audit ledger.

Standard library only. This is intentionally NOT an automatic file organizer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import stat
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS assets (
 id TEXT PRIMARY KEY, first_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS locations (
 path TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(id),
 root TEXT NOT NULL, device TEXT, file_id TEXT, size INTEGER,
 mtime_ns INTEGER, hash TEXT, state TEXT NOT NULL, last_seen TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS loc_asset ON locations(asset_id);
CREATE INDEX IF NOT EXISTS loc_fs ON locations(device, file_id);
CREATE INDEX IF NOT EXISTS loc_hash ON locations(hash);
CREATE TABLE IF NOT EXISTS versions (
 asset_id TEXT NOT NULL REFERENCES assets(id), hash TEXT NOT NULL,
 size INTEGER NOT NULL, first_seen TEXT NOT NULL,
 PRIMARY KEY (asset_id, hash)
);
CREATE TABLE IF NOT EXISTS events (
 id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, asset_id TEXT,
 kind TEXT NOT NULL, detail TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS scans (
 id TEXT PRIMARY KEY, root TEXT NOT NULL, started TEXT NOT NULL,
 finished TEXT, status TEXT NOT NULL, seen INTEGER NOT NULL DEFAULT 0,
 errors INTEGER NOT NULL DEFAULT 0
);
"""

def now():
    return datetime.now(timezone.utc).isoformat()

def canonical(path):
    return str(Path(path).expanduser().absolute())

def connect(db):
    p = Path(db).expanduser().absolute()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=10000")
    conn.executescript(SCHEMA)
    return conn

def event(conn, asset, kind, **detail):
    conn.execute("INSERT INTO events(at,asset_id,kind,detail) VALUES (?,?,?,?)",
                 (now(), asset, kind, json.dumps(detail, sort_keys=True)))

def digest_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def new_asset(conn):
    aid = str(uuid.uuid4())
    conn.execute("INSERT INTO assets(id,first_seen) VALUES (?,?)", (aid, now()))
    return aid

def scan(conn, root, db_path=None):
    root = canonical(root)
    if not os.path.isdir(root):
        raise ValueError("Scan root is not an accessible directory: " + root)
    if os.path.islink(root):
        raise ValueError("Symlink roots are not supported")
    if db_path and os.path.commonpath([root, canonical(db_path)]) == root:
        raise ValueError("Database must be outside scanned root (prevents self-indexing)")
    sid = str(uuid.uuid4())
    conn.execute("INSERT INTO scans(id,root,started,status) VALUES (?,?,?,?)",
                 (sid, root, now(), "running"))
    conn.commit()
    seen = set()
    errors = []
    def walk_error(err):
        errors.append(str(err))
    for current, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        # Never descend into symlinks; count them as explicitly unsupported.
        keep = []
        for name in dirs:
            p = os.path.join(current, name)
            if os.path.islink(p):
                errors.append("Skipped symlink directory: " + p)
            else:
                keep.append(name)
        dirs[:] = keep
        for name in files:
            p = canonical(os.path.join(current, name))
            try:
                before = os.lstat(p)
                if not stat.S_ISREG(before.st_mode):
                    continue
                h = digest_file(p)
                after = os.lstat(p)
                if (before.st_size, before.st_mtime_ns, before.st_ino, before.st_dev) != (
                    after.st_size, after.st_mtime_ns, after.st_ino, after.st_dev
                ):
                    raise OSError("File changed during hashing")
                device, file_id = str(after.st_dev), str(after.st_ino)
                old = conn.execute("SELECT * FROM locations WHERE path=?", (p,)).fetchone()
                if old:
                    aid = old["asset_id"]
                    if old["device"] != device or old["file_id"] != file_id:
                        # Path reuse can represent a new logical asset.
                        aid = new_asset(conn)
                        event(conn, aid, "path_replaced", path=p, previous_asset=old["asset_id"])
                    elif old["hash"] != h:
                        event(conn, aid, "content_changed", path=p,
                              previous_hash=old["hash"], hash=h)
                else:
                    # File IDs can survive renames on the same filesystem. Only
                    # reconcile if exactly one historical match exists AND it is
                    # not concurrently present at another observed path.
                    matches = conn.execute(
                        "SELECT * FROM locations WHERE device=? AND file_id=?",
                        (device, file_id)).fetchall()
                    eligible = [m for m in matches if m["path"] != p and
                                not os.path.exists(m["path"])]
                    if len(matches) == 1 and len(eligible) == 1:
                        m = eligible[0]
                        aid = m["asset_id"]
                        conn.execute("DELETE FROM locations WHERE path=?", (m["path"],))
                        event(conn, aid, "path_changed", old=m["path"], new=p)
                    else:
                        aid = new_asset(conn)
                        event(conn, aid, "discovered", path=p,
                              possible_identity_matches=len(matches))
                conn.execute(
                    """INSERT INTO locations(path,asset_id,root,device,file_id,size,mtime_ns,hash,state,last_seen)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(path) DO UPDATE SET
                      asset_id=excluded.asset_id,root=excluded.root,
                      device=excluded.device,file_id=excluded.file_id,
                      size=excluded.size,mtime_ns=excluded.mtime_ns,hash=excluded.hash,
                      state='present',last_seen=excluded.last_seen""",
                    (p, aid, root, device, file_id, after.st_size, after.st_mtime_ns,
                     h, "present", now()))
                conn.execute(
                    "INSERT OR IGNORE INTO versions(asset_id,hash,size,first_seen) VALUES (?,?,?,?)",
                    (aid, h, after.st_size, now()))
                seen.add(p)
                conn.commit()
            except (OSError, ValueError) as exc:
                errors.append(f"{p}: {exc}")
    # Do not infer file disappearance from an incomplete or failed scan.
    if not errors:
        for row in conn.execute("SELECT path,asset_id,state FROM locations WHERE root=?", (root,)):
            if row["path"] not in seen and row["state"] == "present":
                conn.execute("UPDATE locations SET state='not_observed' WHERE path=?",
                             (row["path"],))
                event(conn, row["asset_id"], "not_observed", path=row["path"],
                      scan=sid)
    else:
        for message in errors:
            event(conn, None, "scan_warning", scan=sid, message=message)
    conn.execute(
        "UPDATE scans SET finished=?,status=?,seen=?,errors=? WHERE id=?",
        (now(), "complete" if not errors else "partial", len(seen), len(errors), sid))
    conn.commit()
    return {"scan": sid, "root": root, "status": "complete" if not errors else "partial",
            "seen": len(seen), "errors": errors[:30], "error_count": len(errors)}

def stats(conn):
    tables = ["assets", "locations", "versions", "events", "scans"]
    out = {t: conn.execute("SELECT COUNT(*) FROM " + t).fetchone()[0] for t in tables}
    out["location_states"] = {r[0]: r[1] for r in conn.execute(
        "SELECT state,COUNT(*) FROM locations GROUP BY state")}
    return out

def main(argv=None):
    ap = argparse.ArgumentParser(description="Continuum — read-only asset registry")
    ap.add_argument("--db", default="continuum.sqlite3", help="SQLite registry path")
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan", help="Inventory a directory without modifying its contents")
    s.add_argument("root")
    sub.add_parser("stats")
    h = sub.add_parser("history")
    h.add_argument("asset_id")
    f = sub.add_parser("find")
    f.add_argument("term", help="Substring in observed path")
    args = ap.parse_args(argv)
    if args.command == "scan":
        # Check before DB initialization to avoid creating the DB in a scan root.
        dbabs = canonical(args.db)
        rt = canonical(args.root)
        if os.path.commonpath([rt, dbabs]) == rt:
            ap.error("Put --db outside the scanned directory")
    with connect(args.db) as conn:
        if args.command == "scan":
            result = scan(conn, args.root, args.db)
        elif args.command == "stats":
            result = stats(conn)
        elif args.command == "history":
            result = [dict(x) for x in conn.execute(
                "SELECT at,kind,detail FROM events WHERE asset_id=? ORDER BY id",
                (args.asset_id,))]
        else:
            result = [dict(x) for x in conn.execute(
                "SELECT * FROM locations WHERE path LIKE ? LIMIT 200",
                ("%" + args.term.replace("%", "\\%").replace("_", "\\_") + "%",))]
    print(json.dumps(result, indent=2))
    if args.command == "scan" and result["status"] != "complete":
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
