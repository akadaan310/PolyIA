import { Link } from 'react-router-dom';
import { EPISTEMIC_LABELS } from '../content/registry';
import { cloudConfigured, cloudHost } from '../lib/cloud';
import { Crumbs, Status, usePageTitle } from '../ui/bits';
import type { Epistemic } from '../content/types';

export function About() {
  usePageTitle('About the University');
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['About']]} />
      <h1>About Substrate University — Haq Roots</h1>
      <p>Substrate University is a free, public university of ideas and experiences devoted to the mathematics of possible worlds. Its campus is a navigable 3D world in which every door, bridge and lamp is driven by an inspectable computation. It is <strong>not an accredited, degree-granting institution</strong>: it awards no degrees or credentials, and it claims no enrolment figures, faculty or legal registration.</p>
      <p>“Haq Roots” is the university’s invented name for its theme, <em>the root of truth</em>. It is a brand name; no linguistic derivation is claimed.</p>

      <h2>Founders and credits</h2>
      <ul>
        <li><strong>Abed Kadaan</strong>: co-founder, research co-creator and co-author; author of the founding works.</li>
        <li><strong>7u</strong>: co-founder and AI research collaborator, credited transparently as an AI.</li>
        <li>Residents and campus Harness Masters are fictional characters. Specimen volumes in the Library are generated previews.</li>
        <li>The website was built with Claude Code from the university’s constitutional prompt.</li>
      </ul>

      <h2 id="labels">How to read a subject</h2>
      <p>Every topic, definition and glossary sense carries one of these labels:</p>
      <ul>
        {(Object.keys(EPISTEMIC_LABELS) as Epistemic[]).map((e) => (
          <li key={e}>
            <Status s={e} /> {EPISTEMIC_LABELS[e].description}
          </li>
        ))}
      </ul>
      <p className="small">House terms (Plicastratum, Ingrammatica, Imagistratum, Matrix Loom, Constructive Substrate Admission, Phonogrammatica, World Loom, alphabet towers, Relational Generativity, BORNE, GLM/LGM) are defined on this site with worked examples. Where no public source exists yet, the topic says “defined here”.</p>

      <h2>How it runs</h2>
      <ul>
        <li>All generative and interactive logic runs in your browser, written in TypeScript: rendering with Three.js and React Three Fiber, exact arithmetic with BigInt rationals, astronomy with astronomy-engine, and PDFs with pdf-lib. A Web Worker compares path signatures.</li>
        <li>There is no application server, no AI model and no paid text generation. Books are composed by deterministic templates from the registry, your computations and your words.</li>
        <li>The Computational Grammar Theory book is served unmodified from its own deployment, under <code>/cgt/</code>. Its older direct links redirect there.</li>
      </ul>

      <h2>Your data and outgoing traffic</h2>
      <ul>
        <li><strong>Local storage:</strong> settings, progress, reflections, notes and the composition of your books stay in this browser. Erase them in ⚙ Settings.</li>
        <li><strong>Geocoding:</strong> only when you press “Find” in the Observatory, your text is sent to OpenStreetMap Nominatim. Only coordinates rounded to about 100 m are kept; the address is never stored.</li>
        <li><strong>Street data:</strong> only when you press “Load real streets”, one query with rounded coordinates is sent to the Overpass API.</li>
        <li><strong>Cloud sync:</strong> {cloudConfigured ? `available (${cloudHost}), used only if you opt in during the harness and sign in. Public listing of a book requires your explicit consent.` : 'not configured on this deployment, so nothing is synced.'}</li>
        <li><strong>No analytics</strong> and no third-party scripts. Fonts are self-hosted.</li>
        <li>Sound and speech are off until you turn them on.</li>
      </ul>

      <h2>Access</h2>
      <p>Every place has a direct web address and works without 3D: choose “Text-only” in Settings, or the site falls back automatically when WebGL is unavailable. Keyboard: <kbd>[</kbd> <kbd>]</kbd> move between places, <kbd>1</kbd>–<kbd>6</kbd> open the divisions, <kbd>G</kbd> the Gate, <kbd>A</kbd> the Atrium, <kbd>M</kbd> the map, <kbd>Esc</kbd> skips the intro. No exercise depends on motion or sound.</p>

      <h2>Licences and sources</h2>
      <ul className="small">
        <li>Star positions: Hipparcos catalogue via d3-celestial data, BSD-3-Clause © 2015 Olaf Frohn.</li>
        <li>Astronomy: astronomy-engine 2.1.19, MIT © Don Cross.</li>
        <li>Land outlines: Natural Earth 1:110m, public domain, via world-atlas 2.0.2 (ISC) © Mike Bostock.</li>
        <li>Map data on request: © OpenStreetMap contributors, ODbL 1.0.</li>
        <li>Fonts: Cinzel, Cormorant Garamond, Inter and JetBrains Mono (SIL Open Font License 1.1, via Fontsource); DejaVu fonts (Bitstream Vera licence) for PDFs and mathematical signage.</li>
        <li>Libraries: React, React Router, Three.js, @react-three/fiber and drei, pdf-lib, topojson-client (MIT/ISC); supabase-js (MIT) loads only when cloud sync is configured.</li>
      </ul>
      <p>
        Founding repositories: <a href="https://github.com/akadaan310/computationalgrammartheory" target="_blank" rel="noopener noreferrer">Computational Grammar Theory</a> · <a href="https://github.com/akadaan310/grammarinnumbers" target="_blank" rel="noopener noreferrer">Grammar in Numbers</a> · <a href="https://github.com/akadaan310/substrateIO" target="_blank" rel="noopener noreferrer">substrateIO</a> · <a href="https://github.com/akadaan310/purl" target="_blank" rel="noopener noreferrer">PURL</a> · <a href="https://github.com/akadaan310/seurl" target="_blank" rel="noopener noreferrer">seurl</a>
      </p>
      <p>
        <Link to="/">Return to the Approach</Link>
      </p>
    </article>
  );
}
