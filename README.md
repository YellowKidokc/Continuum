# Continuum — The Living Archive

> **Nothing lost. Everything connected. Every change accounted for.**

**Status:** Early architecture and development planning. The features described below are design goals, **not yet implemented or validated**.

Continuum is an identity-first, local-first knowledge and file intelligence system. Its purpose is to make a growing collection of documents, research, source code, images, JSON, experiments, and other digital artifacts *traceable, searchable, interconnected, and auditable*—regardless of how they are arranged into folders.

The initial target is a collection of **30,000+ files**, including hundreds or thousands of programs, spread across Windows drives, network storage, repositories, and knowledge vaults.

## The premise

Most file organizers ask: **“Which folder does this belong in?”**

Continuum asks:

1. **What is this artifact?** Establish an identity independent of its current filename or path.
2. **Where has it been?** Record observed locations, versions, and changes.
3. **What does it contain?** Extract searchable information using format-aware processing.
4. **What is it connected to?** Discover and verify relationships with projects, concepts, claims, equations, datasets, programs, and other artifacts.
5. **What do we know—and what are we uncertain about?** Keep evidence, confidence, and unresolved classifications visible.
6. **What changes if this changes?** Track potential downstream dependencies and surface items requiring review.

A file can have multiple meanings and relationships. It should **not** need one permanent folder or one definitive classification to remain discoverable.

## Guiding principle

> **A file may move. Its meaning may change. Its identity and history must remain traceable.**

A pathname is a location, not an identity. A content hash identifies a byte sequence, not necessarily a unique logical document. A model-generated label is an interpretation, not a fact. Continuum keeps these concepts separate.

## Architectural sketch

```text
Windows drives / NAS / repositories / vaults / inboxes
                        |
            Read-only discovery and inventory
                        |
           Identity + provenance registry
          (assets, versions, locations, events)
                        |
      Format-aware extraction / CocoIndex pipelines
                        |
       Search indexes + relationship extraction
                        |
        PostgreSQL + optional vector indexing
                        |
    Virtual views / semantic search / dependency
        explorer / review queue / audit log
```

### Components and responsibilities

| Component | Proposed responsibility |
| --- | --- |
| **Inventory connectors** | Enumerate configured folders, volumes and repositories; record scan coverage and errors. |
| **Identity registry** | Allocate persistent logical asset IDs; store observed filesystem identifiers, paths, cryptographic content hashes and content versions. |
| **Provenance/event ledger** | Record discovery, edits, moves, renames, duplicate observations, missing paths and reconciliation outcomes. Preserve history rather than silently erasing it. |
| **CocoIndex** | Candidate incremental extraction and indexing engine. Reprocess changed inputs and refresh derived search/relationship views. |
| **Format adapters** | Parse text, Markdown, Python/code, JSON/YAML, PDFs, Office files, and image metadata; add OCR where appropriate. |
| **Relationship engine** | Connect artifacts to projects, concepts, definitions, evidence, claims, equations, code dependencies and other artifacts. |
| **Search and views** | Combine exact/path/metadata search with optional full-text, semantic and graph-assisted retrieval. Show multiple virtual collections without moving originals. |
| **Review and audit** | Expose uncertain classifications, missing files, conflicting definitions, and changes that may affect downstream work. |

**Important separation:** CocoIndex is proposed as the *incremental processing layer*, **not** the permanent source of truth for artifact identity or historical events. The registry and event ledger must survive index rebuilds and source synchronization.

## Identity model (proposed)

An artifact record may contain:

```yaml
asset_id: "urn:continuum:asset:example-0001"
display_name: "grace_operator.py"
observations:
  - location: "S:/Research/Experiments/grace_operator.py"
    status: present
content_versions:
  - sha256: "<computed-content-hash>"
    size_bytes: null
relationships:
  - type: related_to
    target: "Grace"
    source: "extraction"
    review_status: unverified
audit:
  - event: discovered
    source: inventory_scan
```

This is an **illustrative schema**, not output from running software.

An asset ID tracks a *logical artifact*. A SHA-256 hash identifies a *particular content version*. Two different logical assets may have identical bytes; one logical asset may have many versions. Renames and moves can often be reconciled using available filesystem IDs, change journals, hashes, and prior observations, but ambiguous situations must be flagged rather than silently merged.

## Safety and integrity rules

**The first release is strictly read-only with respect to source files.**

- Never automatically move, rename, delete, overwrite, or deduplicate source files.
- Never treat AI classification as authoritative identity or permission to mutate files.
- Record errors and uncertainty; do not report incomplete scans as complete.
- Preserve a historical record when a file disappears from an observed path.
- Distinguish **missing**, **offline**, **inaccessible**, **excluded**, and **confirmed deleted**.
- Make every derived classification or relationship traceable to its source and extraction version.
- Keep the registry and indexes separate from original files; support backup and rebuild.
- Avoid uploading private content to external AI services without explicit configuration and consent.
- Require explicit review and a reversible plan before any future write-capable file operations.

**No system can guarantee recovery of arbitrary files from disconnected, unmonitored or destroyed media.** Continuum's practical promise is to detect and disclose loss of visibility, preserve what was previously observed, and verify recoverable copies when backup sources are available. Indexing alone is not backup.

## The distinctive capability: dependency awareness

The long-term aim is more than categorization. If a mathematical axiom, document, dataset or code module is revised, Continuum should be able to identify dependent artifacts that **may** require reevaluation.

Example (hypothetical):

> A change to axiom A8.2 may affect three proofs, four simulations and twelve manuscript passages. Two references may be using older definitions.

This requires explicit, provenance-backed edges and uncertainty handling; proximity in vector space alone does not establish a true dependency.

## Development roadmap

### Milestone 0 — Foundational specification
- [ ] Define the registry, event ledger, stable ID and version semantics.
- [ ] Define scanner permissions, exclusions, symlink handling, offline-volume behavior and security boundaries.
- [ ] Write invariants and failure/recovery tests before ingesting the full archive.

### Milestone 1 — Read-only local prototype
- [ ] Discover and hash a controlled test corpus of about 500 mixed files.
- [ ] Store asset IDs, content hashes, paths, timestamps, sizes and observations.
- [ ] Detect identical-content copies without conflating distinct logical files.
- [ ] Reconcile edits, renames, moves, duplicate copies, inaccessible paths and rescans.
- [ ] Expose an audit trail and report unresolved identity matches.

### Milestone 2 — Search and CocoIndex
- [ ] Evaluate the current supported CocoIndex API against the prototype.
- [ ] Extract text and metadata from supported formats with bounded resource use.
- [ ] Build incremental full-text and optional semantic search.
- [ ] Ensure failed extraction never corrupts the canonical identity ledger.

### Milestone 3 — Relationships and research dossiers
- [ ] Extract candidate relationships and store their evidence and confidence.
- [ ] Support virtual collections, per-asset dossiers and manual corrections.
- [ ] Model definitions, claims, derivations, evidence and dependencies separately.
- [ ] Identify conflicting or stale references for human review.

### Milestone 4 — Scale and operations
- [ ] Benchmark 30,000+ artifacts, including large files and mixed network storage.
- [ ] Add resumable scans, monitoring/reconciliation, checkpointing and recovery.
- [ ] Verify restore procedures and index rebuilds.
- [ ] Build a practical local dashboard and search interface.

### Milestone 5 — Optional controlled actions
- [ ] Design previewable, authorized, logged and reversible plans for organizing files.
- [ ] Keep any write-capable feature disabled until safety acceptance tests pass.

## Initial acceptance tests

A prototype is **not** considered reliable just because it can index a directory. At minimum it must demonstrate:

| Scenario | Expected behavior |
| --- | --- |
| Rename on a monitored volume | Preserve identity when evidence permits; record prior and current paths. |
| Move between monitored directories | Reconcile identity or present an explicit ambiguity. |
| Edit contents | Record a new observed version while retaining history. |
| Create byte-identical copy | Identify matching content without automatically merging logical identities. |
| Disconnect NAS or volume | Mark source unavailable; do not declare every file deleted. |
| Delete or remove a file | Preserve prior record and state what can actually be verified. |
| Parser/model failure | Preserve inventory and integrity records; mark extraction failure. |
| Rebuild search indexes | Preserve permanent identities and audit history. |
| Ambiguous classification | Keep alternatives and evidence; do not fabricate certainty. |
| Interrupted scan | Resume or restart safely; never label a partial scan complete. |

## Candidate technology choices

- **Python:** scanning, adapters, reconciliation and orchestration.
- **PostgreSQL:** authoritative registry, event history, relationship records and queryable metadata.
- **CocoIndex:** incremental extraction and derived indexing, subject to hands-on validation.
- **Full-text/vector search:** retrieval of content and candidate relationships.
- **Windows NTFS change journal:** possible additional change signal where available; periodic reconciliation remains necessary.
- **NAS/network filesystem scans:** coverage-aware polling and reconciliation, because local NTFS-specific assumptions do not apply to every source.

These are starting choices, **not irrevocable dependencies**. Each must justify its complexity through tests.

## What Continuum is not

- Not a script that decides one folder for every file.
- Not an excuse to mass-move or auto-delete irreplaceable research.
- Not a guarantee that AI-generated classifications are correct.
- Not a backup system merely because it remembers file paths or hashes.
- Not yet a functioning application. This repository begins with an engineering charter.

## Project origin

Continuum began as a design conversation about a universal inbox for a large, fragmented personal research and software archive. The goal was to preserve identity, context and continuity without enforcing a rigid taxonomy. The name **Continuum** reflects the central premise: information can change locations, representations and interpretations while its traceable history remains intact.

The initial research collection includes interdisciplinary documents, mathematical formalization, software experiments, and evolving definitions. The architecture is intended to remain domain-neutral so it can also serve other archives.

## Useful references

- [CocoIndex](https://github.com/cocoindex-io/cocoindex) — candidate incremental processing engine.
- [git-annex](https://git-annex.branchable.com/) — useful reference for content-location tracking.
- [TagSpaces](https://www.tagspaces.org/) — useful reference for portable metadata and tagging.
- [Microsoft USN change journal documentation](https://learn.microsoft.com/en-us/windows/win32/fileio/change-journals) — relevant to Windows file-change tracking.

---

**The engineering commitment:** *No AI-generated conclusion, file operation, or indexing failure should silently destroy or overwrite the evidence needed to reconstruct what happened.*
