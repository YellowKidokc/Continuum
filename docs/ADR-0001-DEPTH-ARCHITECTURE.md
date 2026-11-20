# Architecture Decision Record 0001 — Continuum as a Research Depth Resolver

**Decision date:** 2026-11-20  
**Status:** Adopted as working architecture; integrations remain unverified  
**Scope:** Continuum, Faith Through Physics depth navigation, and cross-project interoperability

## What changed

The original Continuum plan emphasized universal file inventory, classification, provenance, and automatic discovery across ~30,000 documents. Those remain important, but **the primary product objective has changed**:

> From the single entry point **"God is"**, a reader must be able to reach the rigorous treatment of any topic in **one or two clicks**, including its published argument, competing explanations, the framework's superseded attempts, audits, unresolved objections, and formal receipts.

Continuum is **not** to become another independent source-of-truth registry, file sorter, manuscript generator, vault, or search index. It is a **cross-system identity and provenance resolver plus navigation/publishing-dependency layer**. The architecture must preserve intellectual lineage, including failures and rejected hypotheses.

Do not add a fourth independent paper-ID system. Use mappings to existing identifiers, retain original values, and require explicit resolution when IDs collide.

## Non-negotiable depth contract

| Layer | Audience / representation | Required connections |
| --- | --- | --- |
| L0 | Root axiom **God is** | Topic directory, provenance, root claim identity |
| L1 | Public HTML story page | Direct links to L2 and L3 (not forced sequential traversal) |
| L2 | Rigorous topic paper | Claims, equations, term-by-term plain-English translations, Scripture, historical witnesses, named critics, audit |
| L3 | Research atlas / topic framework | Relevant schools, strongest objections, earlier internal models, rejected/superseded versions and reasons, open problems |
| L4 | Inspectable receipts | Audits, Lean 4 sources/build reports/axioms, derivations, source records, objections ledger |

**Definition:** "Within two clicks" is a navigation acceptance criterion measured from the L0 topic entry, not a rule to omit evidence or compress analytical depth. L1 should expose direct L2 and L3 links.

**Stub:** An L1 page missing L2/L3 is flagged as a stub, not silently represented as complete.

## Source ownership and division of labor

- **Quantum Paper** (`YellowKidokc/OBS_-Quantum_Paper`): candidate **logical paper identity / virtual folder membership** provider. Existing prototype uses registry IDs and one original Markdown paper shown in multiple locations. Do not assume it handles externally renamed files or concurrent edits safely.
- **David-OSv3** (`YellowKidokc/David-OSv3`): candidate **filesystem observation, works/versions registry, extraction, review/admission workflows, watcher and event infrastructure**. Its Stage 1 registry already has work IDs, versions, review queue, and provenance. Avoid duplicating this without a demonstrated deficiency.
- **Continuum**: **cross-reference mappings** among IDs, typed claim/evidence/version graph, depth navigation, status and blast-radius impact, canonical view projections, and drift detection.
- **Kensaku**: optional local discovery/OCR/search adapter, **not** authoritative for identity or claims.
- **Hister/Nogon Theophysics fork** (`YellowKidokc/hister_fork`): optional managed research intake and retrieval backend. It has a separate content-addressed store and PostgreSQL receipts; its behavior and operating cost need hands-on validation. Upstream license is **AGPLv3**; assess distribution/network-source obligations before copying or embedding code. An AGPL obligation is not a blanket prohibition on usage.
- **CocoIndex**: optional derived incremental extraction/embedding/relationship pipeline **only if the pilot proves a need**. It must never become the canonical identity or audit ledger.

**Smallest working combination:** Quantum Paper IDs + verified David-OSv3 registry + Continuum link resolver. Do not make the first pilot depend on Kensaku, Hister, CocoIndex, or a second database unless acceptance criteria require it.

## Typed links and epistemic discipline

The relationship store should support at least:

`DERIVED_FROM`, `SUPERSEDES`, `REJECTED_BECAUSE`, `OBJECTED_TO_BY`, `SUPPORTED_BY`, `FORMALIZED_BY`, `PUBLISHED_AS`, `REFERENCES`, `DEPENDS_ON`, `TOPIC_HAS_ASSET`, and `HAS_AUDIT`.

Each edge must have:
- source and target identifiers, type, and recorded date;
- exact supporting evidence: source artifact/version plus quote span, code location, or audit receipt;
- origin (human/import/deterministic/parser/AI proposal);
- review state (proposed/confirmed/rejected/contested);
- confidence only if applicable, separate from verification;
- historical validity and supersession info;
- optional direct dependency semantics used for impact analysis.

An AI-suggested relationship must not silently become an established claim, canon ruling, proof, or deletion authorization. Exact SHA-256 identifies bytes, not a unique logical work. Human rulings must survive rescans and reindexing.

## Audit and blast radius

Respect the research workflow's three flags:
- **INERT:** finding true or relevant but no identified dependent work affected;
- **LOCAL:** correction changes a local claim/presentation without requiring known downstream re-evaluation;
- **STRUCTURAL:** specifically named downstream claims/pages/proofs become suspect and require review.

The system may propose a blast radius, but only **confirmed, typed dependency edges** should be presented as established dependencies. Suspected edges get a separate "possible impact" section. Report both the audit's conclusion and limitations. An authoritative tone in the published public page does not remove the responsibility to preserve an inspectable audit.

## One record, many views

The writer/editing authority must be established per record. Generate or resolve:
- stable public HTML pages;
- Obsidian Markdown/MOC links;
- full research dossiers;
- audit/receipts navigation;
from the same underlying authoritative record and recorded version.

No parallel manually edited canonical copies. A revision should invalidate dependent render receipts until rebuilt and verified. Generated views may be cached but carry source version/hash and generator version.

**Security:** no automatic file mutation, canonization, destructive deduplication or external AI upload. Any changes to source files require a separately authorized plan. Do not let a public HTML page expose private local paths or restricted evidence.

## Identity crosswalk, not forced migration

Proposed crosswalk record:
```json
{
  "continuum_entity_id": "urn:continuum:topic:consciousness",
  "external_identifiers": [
    {"system": "quantum-paper", "id": "<existing-id>", "verification": "unverified"},
    {"system": "david-osv3", "id": "<existing-work-id>", "verification": "unverified"}
  ],
  "aliases": ["Consciousness", "The Witness"],
  "resolution_state": "pending_source_verification"
}
```
Never fabricate actual source IDs in pilot output. Unknown IDs stay unknown.

## Pilot decision

**Consciousness is the first end-to-end acceptance fixture** because it has the most developed L3 corpus. Source reported by collaborating AI, **not directly inspected here**:
- `H:\Obsidian\TH_ Conscious theory\`: 85 notes / 12 families; hub `_MOC.md`;
- public consciousness page in rough form;
- Beam IV "The Witness" paper/audit;
- 2025 "biological antenna" model whose rejection history still needs retrieval;
- audit dated 2026-11-19 that reportedly limits Beams I–IV to theism and uses Beam V to address Christianity.

Treat all four as **unverified source-location / content leads**, not as ingested facts or proof. Locate and read exact assets before declaring links functional.

## Six mandatory pilot acceptance tests

1. Resolve actual L1 public page, L2 Beam IV source, and L3 `_MOC.md` via stored identities, including observed source paths and provenance.
2. Navigate L0 topic directory to L3 within at most two clicks; expose direct L2 and L3 links on L1.
3. Display the audited I–IV/V correction **only if the original audit is located and verified**; preserve its exact scope.
4. Show the biological-antenna model's actual source, dated revision and rejection reason, or show an explicit **missing evidence** status.
5. On a **controlled test copy**, update a source and prove both HTML and Obsidian projections detect source-version drift without creating another canonical work.
6. Flag a STRUCTURAL dependency in the test fixture; list exactly verified downstream impact and separate unverified candidate impact.

A passing demo requires reproducible test fixtures, recorded IDs, resolvable links, and no fabricated research contents. Screenshot-only UI claims are insufficient.

## Step zero: David-OSv3 divergence audit

A collaborating AI reports three diverged local checkouts:
- `D:\GitHub\David-OSv3` — current;
- `D:\GitHub\GOLD\David-OSv3` — old copy reportedly containing `schema.py`;
- `D:\GitHub\David-OSv3-fi` — alternate branch;
- and `D:\Schema_Engine\schema.py`.

These paths/contents **were reported by another AI**, not directly accessed in this session. The GitHub default branch inspection confirmed `engine/registry.py`, `engine/sidecar_writer.py`, `engine/rename_applier.py`, and architecture documents; it did **not** establish local drift contents.

**Do not auto-merge or overwrite any checkout.** Audit git remotes, branch/commit hashes, dirty/untracked files, hashes and diffs; copy unique artifacts to a protected comparison directory; test the classifier against HTML titles (a reported CSS-token contamination bug) before porting it. Report a proposed integration PR with source provenance. Require human approval for merges that may change schemas, classifications or source files.

## Explicitly deferred

- automatic folder relocation/deduplication;
- mass migration of all 30,000 files;
- replacing the existing registry or adopting multiple registries as co-equal truth;
- six-way dependency stack;
- full semantic graph from AI extraction without evidence;
- bulk publication;
- automatically adjudicating philosophy, physics or theology;
- production NAS deployment before restoration and security tests.

## Source references

- [David-OSv3 registry](https://github.com/YellowKidokc/David-OSv3/blob/main/engine/registry.py)
- [David-OSv3 Stage 1](https://github.com/YellowKidokc/David-OSv3/blob/main/docs/STAGE1_REGISTRY.md)
- [David-OSv3 CocoIndex admission proposal](https://github.com/YellowKidokc/David-OSv3/blob/main/docs/COCOINDEX_LEAN4_ADMISSION_AND_TAGGING.md)
- [Quantum Paper README](https://github.com/YellowKidokc/OBS_-Quantum_Paper/blob/OBS-Plugin-Final-Claude/README.md)
- [Hister fork research control center](https://github.com/YellowKidokc/hister_fork/blob/master/deploy/theophysics/README.md)

These documents are evidence of code and design *in their repositories*, not proof that the entire integrated system is deployed or passing tests.
