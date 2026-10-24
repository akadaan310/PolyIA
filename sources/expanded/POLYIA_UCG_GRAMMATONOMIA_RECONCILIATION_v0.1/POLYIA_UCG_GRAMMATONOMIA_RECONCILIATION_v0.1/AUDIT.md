# Attachment verification audit — 2026-10-23

## Inputs actually inspected

- `/mnt/data/UCG_FOUNDATIONS.md` — theory summary and reported experimental numbers.
- `/mnt/data/UCG_CODEX_CONSTITUTIONAL_COMMISSION.md` — 156 numbered requirements; all section IDs 001..156 present in sequence.
- `/mnt/data/UCG_SEED_v0.1.zip` — 54 ZIP entries; original contents include source, E01–E05 experiments, data, ledgers and 17-test suite.
- `/mnt/data/GRAMMATONOMIA — The Science of Grammars.md` — proposed language packs, seven language profiles, four levels; no corresponding Wave-1 source or test receipts supplied in this file.
- `/mnt/data/PLICASTRATUM.md`, `/mnt/data/RELATIONAL_GENERATIVITY_FOUNDATION_V0_1.md`, `/mnt/data/GREEK_LATIN_DETERMINATIONS (1).md`, `/mnt/data/corpus engine design (1).md`.
- Existing POLYIA and earlier Division Infinity, Division Knot, Timeless documents for comparison; originals not modified.

## Local execution

Environment: Python local container, NumPy 2.3.5, SymPy 1.14.0, RDKit 2025.09.4; environment differs from Claude's recorded system.

**UCG seed:** `python -m unittest discover -s tests -v`, from an isolated extraction of supplied ZIP: **17/17 passed** in ≈0.39 seconds, with non-fatal unclosed-file warnings. This is a local test run; it does not reproduce all experiment ledgers.

**Fresh replay:** copied extracted source and ran `sh run_all.sh` on the copy only, because script deletes the existing ledger and `.sealed.json` files. E01 and E02 completed; E03 failed with `FileNotFoundError` opening an absolute path `/home/claude/su/att/a5af2628-CHEMISTRATUM_ORGANIC_STRUCTURAL_TABLE_V0_1/organic_structural_atlas/atlas.json` not present in the ZIP. Consequently E04/E05 were not reached by the full-run script in this attempt; **full E01–E05 reproduction is BLOCKED**. The 17 original tests were separately exercised successfully.

**E02 dataset qualification:** `data/g4mp2.json.gz` is referenced by the README but not present in the ZIP. E02 falls back to `data/qm9_le4_subset.json`, a 2,661-byte supplied curated subset. Its measured 48/48 recall is therefore *against that bundled 48-item subset*, not established recall against all QM9 molecules or the full G4MP2 corpus. This is a sample-coverage limitation, not proof of intentional cherry-picking.

**Witness/engine separation violation:** `ucg/molgrammar.py` imports RDKit and invokes its sanitization/canonicalization during prediction generation. Thus the commission's strict “RDKit witnesses only, not engine” constraint is not met in the supplied E02 generator. Resolve by isolating an independently implemented canonical graph representation and using RDKit only downstream as witness, OR amend the claim to “generator uses RDKit normalizer” with appropriate contamination accounting.

**Proleptic limitations:** `ucg/proleptic.py` seals predictions then witnesses and hash-chains a ledger within a single run. It does **not** sandbox reads or independently prove authors had no previous exposure to witness data. `seal` overwrites per-experiment `.sealed.json` and a later `witness` verifies only the latest seal's hash. This is reproducibility/process evidence, not cryptographic proof of blind independent discovery. Upgrade to isolated sealed pre-commit run, read-denied witness mount, immutable runs, external timestamp/signature if warranted, independent holdouts and direct byte verification.

**Scientific witness scope:** UCG's “98/118 configurations,” small molecules and formal-language examples are reported seed findings; some use conventional reference constants, within-run witness libraries or small curated benchmarks. Treat reported counts as candidate reproduction targets and separately re-audit method details before promoting to general scientific capability. In particular “periodic table derived from Z only” uses an explicit special case for helium; the statement should mean *Z plus declared domain rules/exceptions*, not a universal emergence from a bare integer without chemical prior assumptions.

**Muse:** wave-one status states “running, assertions passing,” but only a standalone research paper was supplied here. No Wave-1 code or independently rerunnable package in this specific attachment set. Likewise, the attributed external Perplexity survey needs source snapshots/citations and versioned datasets before claims about 100 language packs become verified.

## Audit verdict

- **PASS**: structural document inspection, 156 commission sections present, 17 UCG seed conformance tests, source separation analysis.
- **PARTIAL**: E01/E02 replay (subject to source-version validation).
- **BLOCKED**: E03 fresh replay (missing absolute atlas path), full E01–E05 chain.
- **NOT RUN**: independent tests of Muse's Wave-1 models; production integration; Oracle VM; POLYIA implementation/deployment; independent peer review.

Avoid treating this audit as a certification that UCG or GRAMMATONOMIA is a deployed universal language/chemistry engine.
