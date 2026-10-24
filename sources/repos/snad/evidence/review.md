# Independent implementation review — 2026-10-18

Review scope: the independent SNAD implementation developed after base `450db7f`, checked against the supplied binding mission brief and `docs/superpowers/specs/2026-10-18-snad-design.md`. This is an automated fresh-context engineering review, not an independent human usability session, linguistic adjudication, legal opinion, or a claim of novel research. The reviewer edited this report only; implementation agents address findings separately.

## Critical

None identified in the inspected implementation. Review is bounded by the checks below and is not a security certification.

## Important findings

1. **Offline package writes followed destination symlinks.** `scripts/mission.ts`, `buildPackage` / `regularFile`. Initial reproduction: make `package/files/input` a symlink to a separate file containing `original`; pack a source file containing `replacement`. The separate file became `replacement`. Source-only path validation did not protect destinations. Replacing the complete `package/files` directory with a symlink to an external directory also produced `verifyPackage(...).valid === true`. Scope: a reused or adversarial package destination could redirect writes or defeat the package boundary. Implementation subsequently added root/ancestor/destination checks and regression tests; final independent recheck is recorded below.

2. **Distinct Unicode referent sets collided.** `packages/snad-core/src/analysis.ts`, referent comparison. `analyze(adaptDialogue([{text:'x',referents:['A\u0000B','C']},{text:'y',referents:['A','B\u0000C']}])).transitions` initially returned `[]`. NUL-delimited joining was not injective over the accepted identifier domain. Scope: an explicit reference change could disappear. The implementation now compares canonical arrays; final independent recheck is recorded below.

3. **Reference set order affected structural equivalence.** `packages/snad-core/src/operators.ts`, `structuralSignature`. The inputs with referents `[A,B]` then `[A]`, versus `[B,A]` then `[A]`, initially had different signatures despite equal reference sets at each position. Detection already treated referents as sets. Scope: false inequivalence under reference permutation. The implementation now uses whole occurrence patterns and version `snad-signature/2`; final independent recheck is recorded below.

4. **Input mode changed export provenance before changing the analysis.** `web/main.ts`, `switchMode` / export handler. From an initial Qur'anic analysis, click “Your own dialogue”, then “Export JSON” before analyzing turns. The download initially had filename `snad-dialogue.json`, user-supplied provenance, and a Qur'anic `analysis.id`. Scope: a portable scientific artifact misrepresented its source. Browser reproduction confirmed this independently; final disposition appears below.

5. **The required multi-ayah example failed in the browser.** `web/main.ts`, `openLocus`. Opening `28:4–5` after `50:2` triggered `Invalid unit quran:28:5:t0 span differs from originalText`, leaving `50:2` displayed. The combined units retained local ayah offsets while metadata retained only the first ayah's `originalText`; strengthened SDK source validation exposed the mismatch. Scope: a mandatory journey failed and range source offsets were inconsistent. Final disposition appears below.

6. **Quotation brackets depicted unsupported containment.** `web/main.ts`, graph frame bands. Every detected quote bracket initially spanned the entire displayed graph even when the frame belonged to only one turn. Scope: the visualization suggested a quotation covered unrelated source units. The count also described first-level frames as “nested”. Requested repair: scope frames to actual units/spans or present an explicit textual frame list rather than unsupported geometry. Final disposition appears below.

7. **Browser accessibility acceptance initially failed.** `web/style.css`, graph SVG roles, guided-button accessible names. The initial browser run had serious axe findings for color contrast, label/content name mismatch, and `role="img"` containing focusable graph buttons. Scope: several controls and the graph were difficult to use with assistive technology. Final disposition appears below.

8. **Strict package verification conflicted with installation instructions.** `scripts/mission.ts`, unlisted-file scan; `docs/handoff.md` and manifest continuation. After the symlink fix, adding the file `files/node_modules/.package-lock.json` caused `verifyPackage` to reject an otherwise unchanged package. The documented journey installed dependencies before verification, which necessarily creates those unlisted files. Scope: a clean recipient following the instructions could not reproduce the claimed verification. Requested repair: dependency-free verification before installation, with an explicit snapshot boundary. Final disposition appears below.

## Minor findings and bounded modeling choices

- The initial `snad-core` tarball contained build outputs and `package.json` but neither an API README nor the MIT license notice. The repository README linked a nonexistent package README. Package-local documentation and notice were requested before delivery.
- Caller-supplied `attribution.frameId` values can identify frames absent from punctuation-derived `frames`. This may be a useful external-frame declaration, but its external/unresolved status must survive in uncertainty and documentation rather than imply a resolved extracted frame. Punctuation extraction is unit-local and does not by itself provide speaker inference or full cross-frame discourse composition.
- `docs/integrations.md` initially described the outcome of PURL discovery as if no standalone ACSP surface had been established, while the newer `docs/acsp.md` documented live ACSP/0.1 discovery. Cross-reference and scope qualification were requested.
- A source-link concern was withdrawn: the actual corpus records use a pinned HTTPS source URL, so the existing branch did not produce the non-HTTP link initially suspected.

## Evidence assessed

- The entire 6,236-record corpus test enumerated unique loci across 114 surahs and compared every stored text string against the pinned upstream snapshot. Short/empty-feature property cases remained valid. The text-only whole-corpus pass reported zero detections without inventing features.
- Existing evidence distinguishes addressable, parsed, analyzed, detected, visualized, and audio-verified counts. The supplied morphology pass reports 2,738 ayahs with 4,929 transitions and zero attribution transitions. None of those numbers establishes a known speaker. No sample or legacy highlight selection substitutes for the corpus domain.
- Core tests exercised identity stability, Unicode IDs, mutation isolation, portable replay, source spans, unknown speakers, nested punctuation, timestamps, topology, and finite path composition. Composition checks are ID-level free-path concatenation checks; they are not a proof about semantic discourse reference.
- The numerical baseline comparison discloses authored supplied-feature gold and its limited purpose. Perfect fit is explicitly not natural-text accuracy or superiority. Twenty candidates are labeled finite observations without novelty claims; negative controls and source-detector mismatches are preserved. Three-language examples explicitly use manual labels and do not claim automatic cross-language generalization.
- Source and data notices separate original MIT code, CC BY-SA text, QAC's original notices and the unlicensed ISNAAD compatibility boundary. QAC mirror agreement is not claimed to be an official digest. This review did not independently resolve the legal effect of the nonstandard notices.
- The PURL evidence and documentation identify `input json` as an identity/transport program. Remote replay does not claim to execute the SNAD SDK. GitHub creation is explicitly blocked by integration HTTP 403. CGIT is a separate artifact service, not Git wire protocol or an anonymous source-host substitute. No remote writes were performed by this reviewer.
- Initial `npm run typecheck` and `npm run build` passed. Initial `npm test` had 32 passes and five missing-ACSP failures while that adapter was still under construction; these transient failures are retained here rather than represented as a final result. Initial browser run had three passes and the range/accessibility failures above.

## Final disposition

**Approve the inspected implementation after repairs. No unresolved Critical or Important finding remains in this review.** Final clean-checkout, artifact regeneration, immutable source pinning, publication checks and recipient continuation rehearsal remain the coordinating agent's release responsibilities.

| Finding | Final status and independently observed evidence |
| --- | --- |
| 1 — package symlinks | Resolved. `node --import tsx --test tests/mission.test.ts` passed all six tests, including destination-link refusal without external overwrite and rejection of a linked `files` root. Source inspection confirms ancestor/root checks apply to both reads and writes. |
| 2 — Unicode referent collision | Resolved. The original NUL-containing witness now produces a `referents` transition. Core regression passes. |
| 3 — reference order | Resolved. Reordered reference sets now have identical `snad-signature/2` signatures. Tests also check duplication and injective identity renaming. |
| 4 — mode/export provenance | Resolved. Independently opening dialogue mode and immediately exporting now returns `analysis.id: user-dialogue` with user-supplied provenance. Export derives its origin from the analyzed input. |
| 5 — multi-ayah source mapping | Resolved. Independently opening `28:4–5` succeeds without browser errors. Its export retains exact per-locus `sourceRecords`, a declared newline composite `originalText`, and every unit's shifted span slices that composite exactly. |
| 6 — quotation containment | Resolved. Unsupported full-path quotation brackets are absent; `web/main.ts` presents explicit unit/span/depth scopes with additional scopes retained in export. |
| 7 — browser accessibility | Resolved for the checked acceptance threshold. A final independent Chromium/axe check of both corpus and analyzed-dialogue states returned zero serious/critical findings and no page errors. This is not a complete accessibility or human usability certification. |
| 8 — pristine verification order | Resolved. The documented next operation runs `node --experimental-strip-types scripts/mission.ts verify --package ..` before installation. The script uses only Node built-ins. A six-test mission run includes an isolated child-process demonstration without installed npm dependencies; strict rejection of later unlisted files remains explicit. |

The combined targeted SDK/ACSP check, `node --import tsx --test tests/core.test.ts tests/integrations.test.ts`, passed **30/30** after repairs. It covers the new identity/source/frame regressions and all five offline ACSP tests. The latest SDK dry pack includes `README.md` and `LICENSE` alongside its typed build outputs. External frame declarations now carry explicit unresolved-frame uncertainty and supplied-declaration provenance rather than invented local containment. The integration documentation now links and qualifies the separate ACSP audit.

One minor wording correction was requested at the end: the graph's descriptive sentence called every punctuation frame “nested”, including depth-one frames. Its explicit unit/span/depth records are accurate; “quotation frames” is the appropriate collective label. No additional implementation or scientific accuracy claim depends on that adjective.

The coordinating agent reported its final complete Node suite, typecheck and browser suite passing; those broader final runs are not substituted for this reviewer's directly observed targeted checks above. This report does not authorize claims of completed human usability, audio verification, linguistic validation, durable remote ownership, or mathematical novelty.

Publication follow-up, 2026-10-18 (coordinator): the owner subsequently created public `akadaan310/snad`. The approved GitHub integration published both preserved histories and read back their refs plus the original frozen source commit. This supersedes the GitHub creation blocker recorded at review time; it does not alter the reviewer's observations or the frozen research evidence. See `publication.json`.
