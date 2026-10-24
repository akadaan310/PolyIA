# Continue SNAD

Start from the separate mission PURL:

https://purls-production.up.railway.app/p/resource_bd80f9093ac5fb3b2d176291

Read its anonymous manifest and replay before trusting a claimed execution. The live PURL runs a typed JSON identity carrier; the actual SDK and research are the source/evidence snapshot referenced by its state. PURL guest ownership expires and cannot create delegated agents. Public reads do not grant writes. The earlier resource `resource_95a5662789076892fe698316` belongs to a previous mission and must remain unchanged.

The public lab and complete frozen package are linked in [release evidence](release.md). Plain HTTP clients may receive Cloudflare 403/error 1010; a normal anonymous Chromium browser successfully retrieved the manifest/archive and verified their hashes. Preserve that failure if it recurs, and use the explicit local offline fallback when browser transport is unavailable.

The offline fallback is `mission/package/manifest.json` next to `mission/package/files/` in the working delivery, or `manifest.json` next to `files/` after extracting the downloadable mission archive. SHA-256 protects integrity against the supplied manifest; it is not a cryptographic signature or proof of publisher identity.

From extracted `files/`:

```sh
node --experimental-strip-types scripts/mission.ts verify --package ..
npm ci
npm test
npm run typecheck
npm run build
npm run benchmark
npm run experiments
npm run test:browser
```

The verifier uses only Node built-ins and runs before dependencies are installed. It deliberately rejects unlisted files, including generated `node_modules` and build outputs, so verify the pristine extracted snapshot first. Use Node 24 (the recorded runtime), or a Node release supporting `--experimental-strip-types`. The package manifest names its exact `sourceCommit` and hashes every included file. Later metadata/publication commits can follow that source snapshot. Browser tests need Chromium; install it using `npx playwright install chromium` if absent. npm commands fetch only pinned development dependencies, write local test/build outputs and do not mutate remote services.

Read `docs/reconstruction.md`, `docs/data-provenance.md`, `docs/foundations.md`, `docs/evidence-report.md`, `docs/research-register.md`, `docs/integrations.md`, and `evidence/publication.json`. Preserve mismatches and negative controls. Original source repositories and FALAK are read-only. Source licenses, QAC mirror uncertainty, partial morphology alignment and absent human/audio verification are material limits.

The next research operation is to measure how conservative withholding of conflicting and unaligned morphology changes transition counts relative to a documented less conservative alignment baseline. It may be run locally; do not change the preserved corpus. Any alternative alignment must be a separate versioned derived object with counterexamples and a comparison against the existing baseline.

The full Git history is published at the public repository https://github.com/akadaan310/snad. Clone it with `git clone https://github.com/akadaan310/snad.git`; `main` contains the full research source and `hosting-preview` preserves the separate deployment history. The owner created the repository after the integration's initial creation attempt returned HTTP 403. That old blocker remains in the frozen snapshot and historical PURL records; current publication evidence supersedes it. All of the owner's repositories must remain public. Use the approved GitHub plugin, including its documented Git transport, for GitHub operations; ask once before using each additional plugin. Do not push SNAD to ISNAAD or reuse an unrelated repository.

For PURL publication, use the inspected launch SDK and a fresh guest or verified principal, inspect scopes, create a separate owned mission/fork, compile, build tests, run, inspect terminal execution/artifact, checkpoint and publish; verify each persisted write by readback. A JSON identity transport test is not an SDK research run. For durable mission ownership, verified owner authentication and delegation support must be provisioned. Follow `docs/integrations.md` and preserve actual failure responses.
