# SNAD

An independent, evidence-preserving SDK and laboratory for attribution and discourse transition grammar. Source grammar, attribution identity, quotation frames and interpretation remain separate. This is a computational research instrument; detected structure does not verify speaker intent.

Mission first: https://purls-production.up.railway.app/p/resource_bd80f9093ac5fb3b2d176291

The PURL is a published typed continuation carrier. Its identity program verifies transport/replay, not execution of the local SNAD SDK. Read [integration evidence](docs/integrations.md) for actual operations and guest-session limits. The complete offline continuation is `mission/manifest.json` plus its packaged `files/` snapshot.

```sh
npm ci
npm test
npm run typecheck
npm run build
npm run dev
npm run benchmark
npm run experiments
npm run test:browser
```

Node 24 is the recorded runtime; Node 22.12+ is required by Vite. Browser tests require Chromium (`npx playwright install chromium`). No accounts or services are needed to use the SDK, run experiments or explore the lab.

On release checkouts, `npm run build` reconstructs the frozen mission download from its recorded Git commit and verifies its file hashes before adding it to the lab. A shallow clone must contain that snapshot commit. Extracted offline snapshots build the standalone lab without requiring Git history.

```ts
import { adaptDialogue, analyze, serialize } from 'snad-core';

const input = adaptDialogue([
  { id: 'a', speaker: 'Mira', text: 'I will bring the book.', features: { person: '1' } },
  { id: 'b', speaker: 'Omar', text: 'You will bring the book.', features: { person: '2' } }
]);
const result = analyze(input);
console.log(result.transitions, serialize(result));
```

The features and identities above are supplied annotations. The SDK does not infer a known speaker from a grammatical pronoun. See [typed APIs](docs/api.md), [nomenclature](docs/nomenclature.md), and the [SDK README](packages/snad-core/README.md).

All 6,236 ayahs across 114 surahs have stable `quran:S:A` addresses, including one-word verses and verses with no detected transition. Text is stored without normalization. Official QAC morphology is a separate source with explicit alignment omissions and conflicts. Addressability, parsing, analysis, detection, visualization and audio verification use separate denominators. Inspect [data provenance](docs/data-provenance.md), [corpus status](evidence/corpus-status.json) and [benchmark](evidence/benchmark.json).

[ISNAAD reconstruction](docs/reconstruction.md) records three branch tips, an exact 1,000-locus highlight baseline and 22 pinned detector fixtures. Original source code is not copied into the generic SDK. ISNAAD is read-only; FALAK is not a dependency. Numerical results, baselines, counterexamples and open hypotheses are in the [evidence report](docs/evidence-report.md) and [research register](docs/research-register.md). No novelty or theorem is claimed from these finite experiments.

The full source and Git history are public at [akadaan310/snad](https://github.com/akadaan310/snad). The owner created the repository after the integration's initial creation attempt was rejected; both `main` and `hosting-preview` were then published and read back through the approved GitHub integration. [Publication evidence](evidence/publication.json) preserves that history. All of the owner's repositories must remain public.

For continuation, read [handoff instructions](docs/handoff.md). Human usability sessions, independent linguistic adjudication and audio verification remain outstanding. Data licenses are separate from the MIT SDK; retain the notices under [data/](data/README.md).

[Live lab](https://snad-discourse-lab.daintyaspen11.chatgpt.site) · [Full frozen source/data/evidence package](https://snad-discourse-lab.daintyaspen11.chatgpt.site/snad-mission.tar.gz) · [Release verification and exact commits](docs/release.md). A fresh-context participant reconstructed the mission from its PURL, verified all 136 packaged files and reproduced the tests/build; see `evidence/continuation-demo.json`.
