# AI developer handoff — Continuum

## Mission

Implement an identity-first, local-first **Living Archive** for tens of thousands of mixed research and software files. Build a trustworthy chain from *physical file observation → persistent logical identity → historical version → extractable contents → candidate relationships → verified dependencies*. Do **not** reorganize files as a shortcut.

## Current implementation

- `continuum.py`: Python standard-library SQLite scanner, SHA-256 observations, distinct logical assets, content version history, event ledger, scan runs, JSON CLI.
- `tests/test_continuum.py`: repeatability, content editing, rename, duplicate, absence, symlinks and database placement tests.
- `QUICKSTART.md`: safe evaluation path.
- `README.md`: project charter, candidate architecture and invariants.

**Critical:** These are initial prototype artifacts, not evidence that a 30,000-file Windows/NAS deployment is reliable. Run and verify tests in the target environment. Do not claim untested behavior.

## Architectural responsibilities

**Continuum core owns:** logical ID, scan observations, provenance, uncertain identity reconciliation, source state, historical events, recoverability metadata, and authorization boundaries.

**Kensaku may own:** fast filename/content/OCR/semantic search via its public CLI or read-only MCP interface. Its search matches are candidates, never identity truth or proof of dependence.

**CocoIndex may own:** incrementally maintained derived extraction pipelines, embeddings, and proposed relationship outputs. Rebuilding/deleting its derived tables must never erase the Continuum identity ledger.

**PostgreSQL may eventually replace SQLite** for service scale, but preserve a storage-agnostic domain model and migrations. Do not introduce it solely to satisfy an architecture diagram.

## Non-negotiable rules

1. Default to read-only access to original files.
2. No background auto-move, rename, delete, overwrite or duplicate removal.
3. No destructive action based on semantic similarity, model confidence, or identical hashes.
4. Every derived relationship must include source evidence, extraction version, review status, and model/config provenance.
5. An inaccessible/offline/partially scanned volume must not be reported as file deletion.
6. Preserve all prior observations, including changed and missing paths.
7. Distinguish file identity, content identity, observed path, and conceptual classification.
8. Fail closed on ambiguity; use a human review queue.
9. Avoid uploading private documents to external services by default.
10. State precisely which requirements are tested and which are only proposed.

## Known limitations requiring correction before scale

- Filesystem inode/device metadata can be unstable or reused. Reliable cross-volume moves are not implemented.
- Scanner has no configurable exclusions, resource budgets, reparse-point policy for Windows, or concurrent-writer lock.
- Under concurrent filesystem changes, a pass can complete without being a consistent snapshot.
- The SQLite event table is append-only by convention, not cryptographically tamper-evident.
- No content extraction, code dependency parser, graph, vector search, UI, NAS adapter, Kensaku adapter, or CocoIndex adapter exists yet.
- `find` is basic path substring retrieval.
- Symlink handling is conservative, not comprehensive.
- Database restore, migration, and Windows/SMB integration tests remain absent.

## Immediate task queue

**P0 — integrity and reproducibility:** run tests; fix failures; CI for Windows/Linux; coverage-aware scanning; file inclusion/exclusion rules; database schema migration; interruption/recovery; stability tests.

**P1 — controlled corpus:** generate a 500-file fixture with varied formats, renamed files, duplicate bytes, edited documents, nested directories, inaccessible paths and simulation of offline shares. Report results with actual counts and exceptions.

**P2 — retrieval adapters:** inspect Kensaku's current CLI/MCP contract and create a guarded adapter; expose search results as references to observed asset IDs where resolvable. Benchmark it and measure overlap with CocoIndex.

**P3 — derived processing:** trial CocoIndex on the controlled corpus; implement extraction outputs with explicit provenance and conflict handling, no destructive synchronization into the canonical registry.

**P4 — relationships and UI:** typed evidence-backed edges, revision impacts, human review, local dashboard.

## Engineering working agreement

For every change: read this file and the README; add failing tests first; preserve data on errors; do not modify user originals; commit implementation and tests together; report exact files changed, commands run, results, known failures, and next tasks. Do not invent a pass or benchmark.

### Definition of done (M1)

- Repeat scan preserves logical identity.
- Content edit adds version without overwriting earlier hashes.
- Rename on supported local filesystem preserves identity or produces explicit ambiguity.
- Identical bytes in distinct paths do not imply a single logical artifact.
- Incomplete/offline scans do not mass-mark paths as missing.
- Original files are never altered.
- Every scan has a visible status and errors.
- Rebuildable derived indexes cannot destroy registry history.

The source of truth is executable behavior plus independently repeatable tests—not the README or a prior AI's assurance.
