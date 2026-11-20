# Continuum M1 quickstart

**Current state:** Read-only Python inventory prototype. This is not a GUI, an automatic organizer, an AI classifier, or a completed Kensaku/CocoIndex integration.

Requires Python 3.10+; no third-party dependencies for the core scanner. Use a test folder containing copies of non-sensitive files first.

## Windows PowerShell

```powershell
git clone https://github.com/YellowKidokc/Continuum.git
cd Continuum
python -m unittest discover -s tests -v

# Use an existing test folder (create it and add test files first).
python continuum.py --db "$env:USERPROFILE\continuum-test.sqlite3" scan "C:\Continuum-Test"

python continuum.py --db "$env:USERPROFILE\continuum-test.sqlite3" stats
python continuum.py --db "$env:USERPROFILE\continuum-test.sqlite3" find ".md"
```

The repository's default branch was originally named `OBS-Plugin-Final-Claude`; clone the actual default branch shown by GitHub. The example does **not** scan your entire computer.

## Safety limits

- The program **never writes to source files**, but it creates/writes the SQLite registry specified by `--db`.
- Store the registry **outside** the scanned directory. The CLI checks this.
- Scanning reads entire file contents to compute SHA-256. Large or protected files can take time; use a limited test directory first.
- It does **not** yet enforce file-size limits, exclusions, authentication, access control, or safe concurrent scans.
- Symlink folders are skipped and cause a partial scan warning. Symlink files are ignored as non-regular files.
- An incomplete scan does not mark files missing.
- A file absent in a complete scan becomes `not_observed`, not “deleted.”
- Move matching uses device/inode IDs where available; network shares, inode reuse, cross-volume moves, and replacement of files can make matching ambiguous. No automatic hash-only merging.
- Source drives that are offline at startup cause the scan to fail rather than produce deletion conclusions.
- Index databases may include names, paths and hashes of private files. Protect access and backup the database.
- A hash proves content equality at the time of observation, not that a file can be recovered.
- A success exit code only means this scan finished without reported errors. It does not prove full filesystem consistency against concurrent changes.

## Commands

`scan PATH` — inventory files, hash, reconcile identity where unambiguous, record observations.

`stats` — return JSON counts and location states.

`find TERM` — simple path substring search, maximum 200 results. Not a substitute for Kensaku.

`history ASSET_ID` — JSON event history for a logical asset.

All command output is JSON so other programs and AI agents can consume it.

## Next engineering checkpoints

1. Fix race conditions and add explicit scan root state, exclusion patterns and file-size budgets.
2. Test interrupted scans, inaccessible subdirectories, moves across volumes, hardlinks and directory renames on actual Windows/SMB.
3. Add snapshot/export and restore tests for the registry.
4. Define Kensaku CLI/MCP adapter contract; do not assume any search result is a verified dependency.
5. Evaluate CocoIndex independently for incremental extraction; do not let derived indexes own the permanent event ledger.
6. Add a minimal local UI *only after* inventory invariants pass.

## Acceptance standard

A downstream developer should be able to run the tests, reproduce results on an isolated folder, identify the boundaries between observations and inferences, and continue without permission to modify originals.
