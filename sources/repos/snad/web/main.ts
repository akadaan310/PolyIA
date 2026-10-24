import './style.css';
import corpusData from '../data/quran.json';
import corpusProvenance from '../data/quran.provenance.json';
import {
  adaptDialogue, adaptQuran, analyze, parseLocus, perturb, structuralSignature,
  type Analysis, type AnalyzedUnit, type DialogueTurn, type DiscourseInput,
  type Evidence, type Perturbation, type QuranRecord,
} from '../packages/snad-core/src/index.js';

type MorphologyEntry = { sourceId: string; status: string; features: [number, NonNullable<QuranRecord['features']>[number]][]; unalignedWords: number; ambiguousWords: number };
const optionalMorphology = import.meta.glob('../data/quran.features.json', { eager: true, import: 'default' });
const morphology = (Object.values(optionalMorphology)[0] ?? {}) as Record<string, MorphologyEntry>;
const optionalStatus = import.meta.glob('../evidence/benchmark.json', { eager: true, import: 'default' });
const corpusStatus = (Object.values(optionalStatus)[0] as { counts?: Record<string, unknown> } | undefined)?.counts;
const corpus = corpusData as QuranRecord[];
const corpusIndex = new Map(corpus.map(record => [`quran:${record.surah}:${record.ayah}`, record]));
const visited = new Set<string>();
const presets = [
  { locus: '11:29', name: 'Hūd', note: 'What identifies an addressee?' },
  { locus: '11:36', name: 'Hūd', note: 'Does person imply a speaker?' },
  { locus: '50:2', name: 'Qāf', note: 'Which cues indicate reported speech?' },
  { locus: '28:4–5', name: 'Al-Qaṣaṣ', note: 'What survives an ayah boundary?' },
];
const exampleDialogue: DialogueTurn[] = [
  { speaker: 'Mira', text: 'I said, “He replied, ‘Wait here.’”', timestamp: { start: 1.25, end: 4.5, unit: 'seconds', original: '00:01.250', uncertainty: 0.1 } },
  { speaker: 'Noor', text: 'We can test that assumption.', timestamp: { start: 4.7, end: 7.2, unit: 'seconds', original: '00:04.700', uncertainty: 0.2 } },
  { speaker: 'Mira', text: 'Who does “we” refer to?', timestamp: { start: 7.4, end: 9.8, unit: 'seconds', original: '00:07.400' } },
];
let currentRecords: QuranRecord[] = [];
let analysis: Analysis;
let selectedUnit = 0;
let selectedTransition = 0;
let currentLocus = '11:29';
let mode: 'quran' | 'dialogue' = 'quran';
let analysisMode: 'quran' | 'dialogue' = 'quran';
let comparison: { perturbation: Perturbation; analysis: Analysis; signatureEqual: boolean } | null = null;

const escape = (value: unknown): string => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]!));
const format = (value: number) => value.toLocaleString('en-US');
const icon = (name: string, size = 18) => {
  const paths: Record<string, string> = {
    arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
    graph: '<rect x="3" y="9" width="5" height="6" rx="1"/><rect x="16" y="3" width="5" height="6" rx="1"/><rect x="16" y="15" width="5" height="6" rx="1"/><path d="M8 12h4m0 0V6h4m-4 6v6h4"/>',
    book: '<path d="M12 5v15m0-15C8 2 3 4 3 4v15s5-2 9 1c4-3 9-1 9-1V4s-5-2-9 1Z"/>',
    flask: '<path d="M9 3h6m-5 0v7L4 20h16l-6-10V3M8 14h8"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-11v1"/>',
    export: '<path d="M12 3v12m-5-5 5 5 5-5M4 15v6h16v-6"/>',
    search: '<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>',
    github: '<path d="M9 21v-4c-4 1-5-2-5-2m11 6v-4c0-1-1-2-1-2 4 0 6-2 6-5 0-2-1-3-2-4 0-1 0-2-1-3-2 0-3 1-3 1a12 12 0 0 0-6 0S7 3 5 3c-1 1-1 2-1 3-1 1-2 2-2 4 0 3 2 5 6 5 0 0-1 1-1 2v4"/>',
    check: '<path d="m5 12 4 4L20 5"/>',
  };
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] ?? paths.info}</svg>`;
};

document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <a class="skip-link" href="#laboratory">Skip to laboratory</a>
  <aside class="sidebar" aria-label="Laboratory navigation">
    <a href="#" class="brand"><span class="brand-symbol" aria-hidden="true"><i></i><i></i><i></i></span><span>SNAD<span class="brand-caption">RESEARCH LABORATORY</span></span></a>
    <div class="sidebar-body">
      <p class="eyebrow sidebar-eyebrow">THE WORKSPACE</p>
      <nav><a class="nav-link active" href="#laboratory">${icon('graph')}<span>Attribution lab</span><span class="nav-dot"></span></a><a class="nav-link" href="#guided">${icon('book')}<span>Guided explorations</span></a><a class="nav-link" href="#methods">${icon('flask')}<span>Methods & evidence</span></a></nav>
      <div class="sidebar-rule"></div>
      <p class="eyebrow sidebar-eyebrow">AN OPEN INSTRUMENT</p>
      <p class="sidebar-note">Follow the evidence.<br>Keep the uncertainty.</p>
      <div class="sidebar-diagram" aria-hidden="true"><span></span><i></i><span></span><i></i><span></span></div>
      <p class="sidebar-fine">A standalone instrument for computational attribution & transition grammar.</p>
    </div>
    <div class="sidebar-bottom"><span class="status-dot"></span><span>Local-first. Reproducible.</span><span class="version">v0.1</span></div>
  </aside>
  <div class="page-shell">
    <header class="topbar"><div class="breadcrumbs">Workspace <span>/</span> <strong>Attribution lab</strong></div><div class="topbar-right"><span class="research-pill"><span class="status-dot"></span> Research preview</span><a href="./snad-mission.tar.gz" aria-label="Download SNAD source package">${icon('export', 19)}</a></div></header>
    <main>
      <section class="intro" aria-labelledby="intro-title"><div><p class="eyebrow"><span class="tiny-line"></span> LANGUAGE. STRUCTURE. EVIDENCE.</p><h1 id="intro-title">Trace the structure.<br><em>Question the attribution.</em></h1></div><div class="intro-aside"><p>Who is speaking? Who is addressed?<br>What does the grammar actually tell us?</p><p class="muted">Explore discourse transitions, inspect their evidence, and put your assumptions to the test.</p><a href="#guided" class="text-link">Start with a guided exploration ${icon('arrow', 16)}</a></div></section>
      <section class="coverage-strip" aria-label="Corpus coverage"><div class="coverage-primary"><span class="coverage-number" data-testid="addressable-count">6,236</span><div><strong>ayahs addressable</strong><span>114 surahs · complete source text</span></div><span class="complete-mark">${icon('check', 14)} Complete</span></div><div class="coverage-cell"><span class="small-metric">6,236 <span>/ 6,236</span></span><span>Text parsed</span></div><div class="coverage-cell"><span class="small-metric" id="analyzed-coverage">—</span><span>Analyzed in corpus pass</span></div><div class="coverage-cell"><span class="small-metric" id="detected-coverage">—</span><span>Ayahs with transitions</span></div><div class="coverage-cell"><span class="small-metric" id="visualized-coverage">1 <span>/ 6,236</span></span><span>Visualized this session</span></div><div class="coverage-cell"><span class="small-metric">0 <span>/ 6,236</span></span><span>Audio verified</span></div></section>
      <section class="laboratory" id="laboratory" aria-labelledby="lab-title">
        <div class="section-heading"><div><span class="section-number">01</span><h2 id="lab-title">The attribution desk</h2><span class="section-subtitle">From source to structure</span></div><button class="button button-quiet" id="export-button">${icon('export', 15)} Export JSON</button></div>
        <div class="desk">
          <div class="desk-toolbar"><div class="mode-switch" role="group" aria-label="Input source"><button id="quran-mode" class="mode-button selected" aria-pressed="true">Qur’anic corpus</button><button id="dialogue-mode" class="mode-button" aria-pressed="false" aria-label="Your own dialogue">Your own dialogue</button></div><form id="locus-form"><label for="locus-input" class="sr-only">Ayah locus</label><span class="lookup-icon">${icon('search', 14)}</span><input id="locus-input" value="11:29" placeholder="Surah:ayah" spellcheck="false" autocomplete="off"/><button type="submit" class="lookup-submit" aria-label="Open passage">${icon('arrow', 17)}</button></form></div>
          <div id="lookup-error" class="error-message" role="alert" hidden></div>
          <div id="dialogue-editor" class="dialogue-editor" hidden><div class="editor-heading"><div><h3>Bring a conversation to the desk</h3><p>One object per turn. Speaker labels are supplied observations; timestamps and uncertainty survive export.</p></div><span class="tag">LOCAL ONLY</span></div><label for="dialogue-input">Dialogue turns (JSON)</label><textarea id="dialogue-input" rows="8" spellcheck="false"></textarea><div class="editor-actions"><span>Accepted: text, speaker, addressee, features, timestamp, evidence.</span><button id="analyze-dialogue" class="button button-primary">Analyze dialogue ${icon('arrow', 15)}</button></div><div id="dialogue-error" role="alert" class="error-message" hidden></div></div>
          <div class="desk-columns"><section class="source-panel" aria-labelledby="source-title"><div class="panel-eyebrow"><span class="eyebrow">SOURCE PASSAGE</span><span class="tag">OBSERVED</span></div><div class="source-heading"><h3 id="source-title">Hūd <span data-testid="source-locus">11:29</span></h3><span id="source-language">ARABIC · UTHMANI</span></div><p class="source-instruction">Select a word to inspect its source span.</p><div class="source-text" data-testid="source-text" lang="ar" dir="rtl"></div><div class="source-footer"><span class="preserved-dot"></span><span id="source-preservation">Original orthography preserved</span><a id="source-link" href="${escape(corpusProvenance.source.url)}" target="_blank" rel="noreferrer">Source ↗</a></div><div class="span-detail" data-testid="span-detail"></div></section>
          <section class="path-panel" aria-labelledby="path-title"><div class="panel-eyebrow"><span class="eyebrow">ATTRIBUTION PATH</span><span class="derived-label"><span></span> Derived structure</span></div><div class="path-heading"><h3 id="path-title">A path through the passage</h3><button class="icon-button" id="path-help" aria-label="Explain attribution path">${icon('info', 16)}</button></div><p class="path-subtitle" data-testid="analysis-label">Grammatical person and attribution are separate layers.</p><div id="path-graph" class="path-graph"></div><p class="path-description" data-testid="path-description"></p><div class="path-legend"><span><i class="legend-person"></i>Grammatical person</span><span><i class="legend-frame"></i>Quotation frame</span><span><i class="legend-unknown"></i>Unresolved identity</span></div><div class="path-stats"><div><strong id="unit-count">—</strong><span>source units</span></div><div><strong id="transition-count">—</strong><span>transitions</span></div><div><strong data-testid="frame-count">—</strong><span>quote frames</span></div><div><strong id="unresolved-count">—</strong><span>unresolved speakers</span></div></div></section></div>
          <section class="transition-panel" aria-labelledby="transition-title"><div class="transition-heading"><div class="transition-label"><span class="mini-line"></span><h3 id="transition-title">Inspect the evidence</h3></div><label class="transition-select-label">Transition <select id="transition-select" aria-label="Inspect transition"></select></label></div><div id="transition-detail"></div></section>
        </div>
      </section>
      <div class="below-desk"><section class="perturb-panel" aria-labelledby="perturb-title"><div class="panel-heading"><span class="section-number">02</span><h2 id="perturb-title">Test an alternative</h2><span class="small-tag">PERTURBATION FORGE</span></div><p>Change one assumption. See which structures survive.</p><div class="perturb-controls"><label for="perturbation" class="sr-only">Perturbation</label><select id="perturbation"><option value="drop-features">Remove grammatical features</option><option value="mask-speakers">Mask speakers</option><option value="reverse-units">Reverse source units</option></select><button class="button button-primary" id="compare-button">Run comparison ${icon('arrow', 15)}</button></div><div class="comparison-result" data-testid="comparison-result"><span class="comparison-idle">${icon('flask', 17)} A counterfactual belongs beside every claim.</span></div></section><section class="uncertainty-panel" data-testid="uncertainty-panel" aria-labelledby="uncertainty-title"><div class="panel-heading"><span class="uncertainty-symbol">?</span><h2 id="uncertainty-title">Uncertainty is part of the result.</h2></div><p>A change in grammatical person does not establish a change of speaker. Identities remain unresolved unless the input explicitly supplies them.</p><div class="evidence-key"><span><i class="evidence-observed"></i>Observed</span><span><i class="evidence-derived"></i>Derived</span><span><i class="evidence-hypothesis"></i>Hypothesis</span><span><i class="evidence-interpretation"></i>Interpretation</span></div><span class="uncertainty-count" id="uncertainty-count"></span></section></div>
      <section class="guided-section" id="guided" aria-labelledby="guided-title"><div class="section-heading"><div><span class="section-number">03</span><h2 id="guided-title">A few places to begin</h2><span class="section-subtitle">Four questions, one instrument</span></div><span class="muted tiny-text">Then explore any of the 6,236 ayahs.</span></div><div class="guided-grid">${presets.map((preset, index) => `<button class="guided-card ${index === 0 ? 'selected' : ''}" data-locus="${preset.locus}"><span class="guided-top"><span class="eyebrow">EXPLORATION 0${index + 1}</span>${icon('arrow', 16)}</span><strong>${preset.name} <span>${preset.locus}</span></strong><span class="guided-note">${preset.note}</span><span class="guided-bottom">Inspect passage <i>↗</i></span><span class="sr-only">Explore ${preset.locus}</span></button>`).join('')}</div></section>
      <section class="methods-section" id="methods" aria-labelledby="methods-title"><div><span class="eyebrow">A NOTE ON THE INSTRUMENT</span><h2 id="methods-title">Structure is evidence.<br>Interpretation is a further step.</h2></div><div class="methods-copy"><p>SNAD traces typed discourse transitions from preserved source text and explicitly attributed annotations. Quotation cues are heuristics. Confidence grades evidence quality; it is not a calibrated probability of truth.</p><p id="morphology-notice">Source text: Risan Bagja Pradana’s quran-json v3.1.2 (CC BY-SA 4.0), credited upstream to The Noble Qur’an Encyclopedia. Grammatical annotations, when available, are separate evidence.</p><div class="method-links"><a href="https://purls-production.up.railway.app/p/resource_bd80f9093ac5fb3b2d176291" target="_blank" rel="noreferrer">Live mission PURL ↗</a><a href="./mission/manifest.json">Offline manifest ↗</a><a href="./snad-mission.tar.gz">Code & evidence ↓</a></div></div></section>
      <footer><span><strong>SNAD</strong> &nbsp; Computational attribution & transition grammar</span><span>Made for questions that can be tested.</span></footer>
    </main>
  </div><div id="toast" role="status" class="toast" hidden></div>`;

const $ = <T extends HTMLElement = HTMLElement>(selector: string) => document.querySelector<T>(selector)!;
$('#dialogue-input').textContent = JSON.stringify(exampleDialogue, null, 2);

function openLocus(value: string) {
  const match = value.trim().match(/^(?:quran:)?(\d+):(\d+)(?:[–-](\d+))?$/);
  if (!match) throw new Error('No ayah at that locus. Use surah:ayah, for example 20:1.');
  const parsed = parseLocus(`quran:${match[1]}:${match[2]}`);
  const end = match[3] ? Number(match[3]) : parsed.ayah;
  if (end < parsed.ayah || end - parsed.ayah > 20) throw new Error('No ayah range found. Choose up to 21 consecutive ayahs.');
  const records: QuranRecord[] = [];
  for (let ayah = parsed.ayah; ayah <= end; ayah++) {
    const record = corpusIndex.get(`quran:${parsed.surah}:${ayah}`);
    if (!record) throw new Error('No ayah at that locus. The corpus contains 114 surahs; check the surah and ayah.');
    records.push(record);
  }
  const inputs = records.map(record => {
    const entry = morphology[`quran:${record.surah}:${record.ayah}`];
    const annotation = entry?.features.map(([tokenIndex, features]) => ({ tokenIndex, features, evidence: [{ id: `qac:${record.surah}:${record.ayah}:${tokenIndex + 1}`, status: 'derived' as const, method: 'qac-tag-projection-v1', sourceId: entry.sourceId, note: 'QAC 0.4 grammatical annotation; exact aligned source token. Aggregate fields with conflicting segments are withheld. Not speaker evidence.' }] }));
    return adaptQuran({ ...record, morphology: annotation });
  });
  let sourceOffset = 0;
  const sourceRecords = records.map(record => {
    const start = sourceOffset;
    sourceOffset += record.text.length + 1;
    return { id: `quran:${record.surah}:${record.ayah}`, text: record.text, start, end: start + record.text.length };
  });
  const input: DiscourseInput = { ...inputs[0], id: inputs.length === 1 ? inputs[0].id : `quran:${parsed.surah}:${parsed.ayah}-${end}`, units: inputs.flatMap((item, index) => item.units.map(unit => ({ ...unit, ...(unit.span ? { span: { start: unit.span.start + sourceRecords[index].start, end: unit.span.end + sourceRecords[index].start } } : {}) }))), metadata: { ...inputs[0].metadata, originalText: records.map(record => record.text).join('\n'), sourceRecords, loci: sourceRecords.map(record => record.id) } };
  currentRecords = records;
  currentLocus = `${parsed.surah}:${parsed.ayah}${end === parsed.ayah ? '' : `–${end}`}`;
  records.forEach(record => visited.add(`quran:${record.surah}:${record.ayah}`));
  setAnalysis(analyze(input));
  $<HTMLInputElement>('#locus-input').value = currentLocus;
  document.querySelectorAll<HTMLButtonElement>('[data-locus]').forEach(button => button.classList.toggle('selected', button.dataset.locus === currentLocus));
}

function setAnalysis(next: Analysis) {
  analysis = next;
  analysisMode = next.input.source.kind === 'quran' ? 'quran' : 'dialogue';
  selectedUnit = 0;
  selectedTransition = 0;
  comparison = null;
  renderSource();
  renderGraph();
  renderSpan();
  renderTransition();
  renderComparison();
  $('#visualized-coverage').innerHTML = `${format(visited.size)} <span>/ 6,236</span>`;
  $('#uncertainty-count').textContent = `${format(analysis.uncertainty.length)} explicit uncertainty entries in this analysis`;
}

function renderSource() {
  const preset = presets.find(item => item.locus === currentLocus);
  const title = analysisMode === 'dialogue' ? 'Your dialogue' : (preset?.name ?? `Surah ${currentRecords[0].surah}`);
  $('#source-title').innerHTML = `${escape(title)} <span data-testid="source-locus">${analysisMode === 'quran' ? escape(currentLocus) : `${analysis.units.length} turns`}</span>`;
  $('#source-language').textContent = analysisMode === 'quran' ? 'ARABIC · UTHMANI' : 'USER-SUPPLIED · VERBATIM';
  const source = $('[data-testid="source-text"]');
  source.setAttribute('dir', analysisMode === 'quran' ? 'rtl' : 'auto');
  source.setAttribute('lang', analysisMode === 'quran' ? 'ar' : 'en');
  source.classList.toggle('dialogue-source', analysisMode === 'dialogue');
  if (analysisMode === 'quran') {
    let offset = 0;
    source.innerHTML = currentRecords.map(record => {
      const recordInput = adaptQuran(record);
      const html = recordInput.units.map((unit, index) => `<button class="source-token ${offset + index === selectedUnit ? 'selected' : ''}" data-unit="${offset + index}" aria-label="Inspect source word ${offset + index + 1}: ${escape(unit.text)}" aria-pressed="${offset + index === selectedUnit}">${escape(unit.text)}</button>`).join(' ');
      offset += recordInput.units.length;
      return `<div class="ayah-line">${html}<span class="ayah-marker" aria-label="Ayah ${record.ayah}">۝${record.ayah.toLocaleString('ar')}</span></div>`;
    }).join('');
  } else {
    source.innerHTML = analysis.units.map((unit, index) => `<button class="dialogue-turn ${index === selectedUnit ? 'selected' : ''}" data-unit="${index}" aria-pressed="${index === selectedUnit}"><span class="turn-meta">${escape(unit.attribution.speaker.label ?? 'Unknown speaker')} <time>${escape(unit.timestamp?.original ?? '')}</time></span><span>${escape(unit.text)}</span></button>`).join('');
  }
  $('#source-preservation').textContent = analysisMode === 'quran' ? 'Original orthography preserved' : 'Original turns & timestamps preserved';
  const sourceLink = $<HTMLAnchorElement>('#source-link');
  sourceLink.hidden = analysisMode === 'dialogue';
  sourceLink.href = typeof currentRecords[0]?.source === 'string' ? currentRecords[0].source : corpusProvenance.source.url;
}

function personLabel(unit: AnalyzedUnit) { return unit.features.person ? `${unit.features.person}${({ '1': 'st', '2': 'nd', '3': 'rd' } as Record<string, string>)[unit.features.person]} person` : 'Unannotated'; }
function speakerLabel(unit: AnalyzedUnit) { return unit.attribution.speaker.status === 'known' ? unit.attribution.speaker.label ?? unit.attribution.speaker.id : 'Unresolved'; }

function renderGraph() {
  const count = analysis.units.length;
  const candidateIndices = count <= 4 ? analysis.units.map((_, index) => index) : [...new Set([0, Math.floor((count - 1) / 3), Math.floor((count - 1) * 2 / 3), count - 1])];
  if (!candidateIndices.includes(selectedUnit) && candidateIndices.length > 1) candidateIndices[Math.floor(candidateIndices.length / 2)] = selectedUnit;
  candidateIndices.sort((a, b) => a - b);
  const width = 710;
  const x = (index: number) => candidateIndices.length === 1 ? width / 2 - 72 : 7 + index * (width - 160) / (candidateIndices.length - 1);
  const nodes = candidateIndices.map((unitIndex, nodeIndex) => {
    const unit = analysis.units[unitIndex];
    const person = unit.features.person ?? 'unknown';
    return `<g class="graph-node ${selectedUnit === unitIndex ? 'selected' : ''} person-${person}" transform="translate(${x(nodeIndex)},70)" role="button" tabindex="0" data-unit="${unitIndex}"><text class="graph-unit" x="72" y="-14" text-anchor="middle">UNIT ${String(unitIndex + 1).padStart(2, '0')}</text><rect width="145" height="83" rx="6"/><circle cx="17" cy="25" r="3"/><text class="graph-person" x="28" y="30">${escape(personLabel(unit))}</text><text class="graph-speaker" x="14" y="57">${escape(speakerLabel(unit).slice(0, 16))}</text><text class="graph-token" x="72" y="115" text-anchor="middle" direction="${analysisMode === 'quran' ? 'rtl' : 'ltr'}">${escape(unit.text.length > 17 ? `${unit.text.slice(0, 15)}…` : unit.text)}</text></g>`;
  }).join('');
  const edges = candidateIndices.slice(0, -1).map((from, index) => {
    const to = candidateIndices[index + 1];
    const changes = analysis.transitions.filter(transition => analysis.units.slice(from + 1, to + 1).some(unit => unit.id === transition.to));
    const label = `${changes.length} Δ`;
    return `<path class="graph-edge ${changes.length ? 'changed' : ''}" d="M ${x(index) + 147} 112 L ${x(index + 1) - 4} 112" marker-end="url(#arrow-head)"/><text class="graph-edge-label" x="${(x(index) + 147 + x(index + 1) - 4) / 2}" y="96" text-anchor="middle">${label}</text>`;
  }).join('');
  const frames = analysis.frames.filter(frame => frame.depth > 0);
  const frameList = frames.length ? `<div class="quote-frame-list" aria-label="Quotation frame scopes">${frames.slice(0, 4).map(frame => `<span><strong>Quote depth ${frame.depth}</strong> · unit ${analysis.units.findIndex(unit => unit.id === frame.unitId) + 1} · span [${frame.span.start}, ${frame.span.end}) · cue “${escape(frame.cue)}”</span>`).join('')}${frames.length > 4 ? `<span>${frames.length - 4} additional scopes in export.</span>` : ''}</div>` : '';
  $('#path-graph').innerHTML = `<svg viewBox="0 0 ${width} 230" role="group" aria-label="Attribution path, ${count} source units, ${analysis.transitions.length} transitions. Speaker identities and person features are separate."><defs><marker id="arrow-head" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="none" stroke="#82958a"/></marker></defs>${edges}${nodes}</svg>${frameList}`;
  $('[data-testid="path-description"]').textContent = `${count > 4 ? `Showing ${candidateIndices.length} of ${count} source units. ` : ''}${analysis.transitions.length} typed transitions; ${frames.length} quotation frames. Edge counts (Δ) summarize changes between displayed units. ${analysis.units.every(unit => unit.attribution.speaker.status === 'unknown') ? 'All speaker identities remain unresolved.' : 'Speaker labels are supplied by the input.'}`;
  $('[data-testid="analysis-label"]').textContent = analysisMode === 'dialogue' ? 'Your dialogue · explicit labels, preserved timestamps' : 'Grammatical person and attribution are separate layers.';
  $('#unit-count').textContent = String(count);
  $('#transition-count').textContent = String(analysis.transitions.length);
  $('[data-testid="frame-count"]').textContent = String(analysis.frames.filter(frame => frame.depth > 0).length);
  $('#unresolved-count').textContent = String(analysis.units.filter(unit => unit.attribution.speaker.status === 'unknown').length);
}

function renderSpan() {
  const unit = analysis.units[selectedUnit];
  if (!unit) return;
  const features = Object.entries(unit.features).filter(([, value]) => value !== undefined);
  $('[data-testid="span-detail"]').innerHTML = `<div class="span-detail-heading"><span class="eyebrow">SOURCE SPAN ${unit.span ? `[${unit.span.start}, ${unit.span.end})` : '· TURN'}</span><span class="unit-id">UNIT ${String(selectedUnit + 1).padStart(2, '0')}</span></div><div class="span-values"><span><small>Grammatical person</small><strong>${escape(unit.features.person ? personLabel(unit) : 'Unannotated')}</strong></span><span><small>Attributed speaker</small><strong>${escape(speakerLabel(unit))}</strong></span></div>${features.length ? `<p class="feature-list">${features.map(([key, value]) => `${escape(key)}: ${escape(value)}`).join(' &nbsp;·&nbsp; ')}</p>` : '<p class="feature-list">No grammatical features supplied for this unit.</p>'}${unit.timestamp ? `<p class="timestamp-note">Timestamp: ${escape(unit.timestamp.original ?? unit.timestamp.start)}${unit.timestamp.uncertainty ? ` · ±${escape(unit.timestamp.uncertainty)} ${escape(unit.timestamp.unit ?? '')}` : ''}</p>` : ''}`;
}

function evidenceMarkup(evidence: Evidence[]) {
  if (!evidence.length) return '<p class="muted">No feature evidence attached. The absence of a detected transition is not a semantic claim.</p>';
  const unique = [...new Map(evidence.map(item => [item.id, item])).values()];
  return unique.slice(0, 5).map(item => `<div class="evidence-row"><span class="tag evidence-tag">${escape(item.status)}</span><div><strong>${escape(item.method)}</strong><p>${escape(item.note ?? item.sourceId)}</p><code>${escape(item.sourceId)}</code></div></div>`).join('') + (unique.length > 5 ? `<p class="muted tiny-text">${unique.length - 5} more evidence entries in JSON export.</p>` : '');
}

function renderTransition() {
  const select = $<HTMLSelectElement>('#transition-select');
  select.disabled = !analysis.transitions.length;
  select.innerHTML = analysis.transitions.length ? analysis.transitions.map((transition, index) => `<option value="${index}" ${index === selectedTransition ? 'selected' : ''}>${String(index + 1).padStart(2, '0')} · ${escape(transition.kinds.join(' + '))}</option>`).join('') : '<option>No typed transition detected</option>';
  const transition = analysis.transitions[selectedTransition];
  if (!transition) {
    $('#transition-detail').innerHTML = `<div class="empty-evidence"><div><span class="empty-glyph">∅</span><strong>No typed transition detected in this input.</strong><p>${morphology[currentRecords[0]?.id ?? ''] ? 'Available morphology was analyzed; no changing adjacent feature was detected.' : 'Without source-backed changing features, the instrument reports an empty transition set.'}</p></div><div class="empty-note"><span class="tag">EXPLICIT LIMIT</span><p>Source units are still addressable. A zero is a valid computational result; speaker identity remains uncertain.</p></div></div>`;
    return;
  }
  const from = analysis.units.find(unit => unit.id === transition.from)!;
  const to = analysis.units.find(unit => unit.id === transition.to)!;
  $('#transition-detail').innerHTML = `<div class="transition-grid"><div class="transition-summary"><div class="transition-badge">${escape(transition.kinds.join(' + '))}</div><div class="transition-pair"><span dir="auto">${escape(from.text.length > 35 ? from.text.slice(0, 32) + '…' : from.text)}</span>${icon('arrow', 17)}<span dir="auto">${escape(to.text.length > 35 ? to.text.slice(0, 32) + '…' : to.text)}</span></div><p>Person: <strong>${escape(from.features.person ?? '?')} → ${escape(to.features.person ?? '?')}</strong> <span class="transition-separator">|</span> Speaker: <strong>${transition.kinds.includes('speaker') ? 'label changed' : 'no established change'}</strong></p><span class="quality-label">Evidence quality ${transition.confidence.toFixed(2)} · uncalibrated</span></div><div class="transition-evidence">${evidenceMarkup(transition.evidence)}</div></div>`;
}

const perturbationNames: Record<Perturbation['kind'], string> = { 'drop-features': 'Remove grammatical features', 'mask-speakers': 'Mask speakers', 'reverse-units': 'Reverse source units' };
function renderComparison() {
  if (!comparison) {
    $('[data-testid="comparison-result"]').innerHTML = `<span class="comparison-idle">${icon('flask', 17)} A counterfactual belongs beside every claim.</span>`;
    return;
  }
  $('[data-testid="comparison-result"]').innerHTML = `<div class="comparison-heading"><strong>${escape(perturbationNames[comparison.perturbation.kind])}</strong><span class="tag">SEED ${comparison.perturbation.seed}</span></div><div class="comparison-numbers"><span><small>Original</small><strong>${analysis.transitions.length} <i>transitions</i></strong></span><span class="comparison-arrow">→</span><span><small>Perturbed</small><strong>${comparison.analysis.transitions.length} <i>transitions</i></strong></span></div><p>${comparison.signatureEqual ? 'Structural signature retained.' : 'Structural signature changed.'} This compares typed structure, not meaning or speaker intention.</p>`;
}

function selectUnit(index: number) {
  if (!analysis.units[index]) return;
  selectedUnit = index;
  const transitionIndex = analysis.transitions.findIndex(transition => transition.from === analysis.units[index].id || transition.to === analysis.units[index].id);
  if (transitionIndex >= 0) selectedTransition = transitionIndex;
  const restoreGraphFocus = document.activeElement?.tagName.toLowerCase() === 'g';
  const restoreSourceFocus = document.activeElement?.closest('[data-testid="source-text"]');
  renderSource(); renderSpan(); renderGraph(); renderTransition();
  if (restoreGraphFocus) document.querySelector<SVGElement>(`g[data-unit="${index}"]`)?.focus();
  else if (restoreSourceFocus) document.querySelector<HTMLButtonElement>(`[data-testid="source-text"] [data-unit="${index}"]`)?.focus();
}

function switchMode(next: 'quran' | 'dialogue') {
  mode = next;
  $('#dialogue-editor').hidden = mode !== 'dialogue';
  $('#locus-form').hidden = mode === 'dialogue';
  $('#quran-mode').classList.toggle('selected', mode === 'quran');
  $('#dialogue-mode').classList.toggle('selected', mode === 'dialogue');
  $('#quran-mode').setAttribute('aria-pressed', String(mode === 'quran'));
  $('#dialogue-mode').setAttribute('aria-pressed', String(mode === 'dialogue'));
  if (mode === 'quran') openLocus(currentLocus);
  else $('#analyze-dialogue').click();
}

document.addEventListener('click', event => {
  const target = event.target as Element;
  const unit = target.closest<HTMLElement>('[data-unit]');
  if (unit) selectUnit(Number(unit.dataset.unit));
  const preset = target.closest<HTMLButtonElement>('[data-locus]');
  if (preset) { switchMode('quran'); openLocus(preset.dataset.locus!); $('#laboratory').scrollIntoView({ behavior: 'smooth', block: 'start' }); }
});
document.addEventListener('keydown', event => {
  const target = (event.target as Element).closest<HTMLElement>('g[data-unit]');
  if (target && (event.key === 'Enter' || event.key === ' ')) { event.preventDefault(); selectUnit(Number(target.dataset.unit)); }
});
$('#locus-form').addEventListener('submit', event => {
  event.preventDefault();
  try { openLocus($<HTMLInputElement>('#locus-input').value); $('#lookup-error').hidden = true; }
  catch (error) { $('#lookup-error').textContent = error instanceof Error && /No ayah/.test(error.message) ? error.message : 'No ayah at that locus. Use surah:ayah, for example 20:1.'; $('#lookup-error').hidden = false; }
});
$('#quran-mode').addEventListener('click', () => switchMode('quran'));
$('#dialogue-mode').addEventListener('click', () => { switchMode('dialogue'); $<HTMLTextAreaElement>('#dialogue-input').focus(); });
$('#analyze-dialogue').addEventListener('click', () => {
  try {
    const turns: unknown = JSON.parse($<HTMLTextAreaElement>('#dialogue-input').value);
    if (!Array.isArray(turns) || !turns.length || turns.length > 200 || turns.some(turn => !turn || typeof turn.text !== 'string')) throw new Error('Supply an array of 1–200 turns, each with a text string.');
    setAnalysis(analyze(adaptDialogue(turns as DialogueTurn[], { id: 'user-dialogue', kind: 'user-supplied', title: 'Your dialogue' })));
    $('#dialogue-error').hidden = true;
    $('#lookup-error').hidden = true;
  } catch (error) { $('#dialogue-error').textContent = error instanceof Error ? error.message : 'Could not read this dialogue.'; $('#dialogue-error').hidden = false; }
});
$('#transition-select').addEventListener('change', event => { selectedTransition = Number((event.target as HTMLSelectElement).value); renderTransition(); });
$('#compare-button').addEventListener('click', () => {
  const perturbation: Perturbation = { kind: $<HTMLSelectElement>('#perturbation').value as Perturbation['kind'], seed: 42 };
  const perturbed = analyze(perturb(analysis.input, perturbation));
  comparison = { perturbation, analysis: perturbed, signatureEqual: structuralSignature(analysis) === structuralSignature(perturbed) };
  renderComparison();
});
$('#export-button').addEventListener('click', () => {
  const artifact = { schemaVersion: 'snad.lab-export/1', exportedAt: new Date().toISOString(), analysis, comparison, sourceProvenance: analysisMode === 'quran' ? corpusProvenance : { source: 'user-supplied', privacy: 'This export contains the dialogue you entered.' }, coverage: { addressable: corpus.length, textParsed: corpus.length, visualizedThisSession: visited.size, audioVerified: 0 }, notice: 'Grammatical person does not establish speaker identity. Evidence quality is uncalibrated.' };
  const url = URL.createObjectURL(new Blob([JSON.stringify(artifact, null, 2)], { type: 'application/json' }));
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = `snad-${analysisMode === 'quran' ? currentLocus.replace(/[:–]/g, '-') : 'dialogue'}.json`; anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 3000);
});
$('#path-help').addEventListener('click', () => {
  const toast = $('#toast'); toast.textContent = 'Nodes show source units. Edges follow source order; “changes” counts detected typed transitions between displayed units. Quotation frames are heuristic. Select a node to inspect its source.'; toast.hidden = !toast.hidden;
});

openLocus('11:29');
if (corpusStatus) {
  const count = (key: string) => typeof corpusStatus[key] === 'number' ? format(corpusStatus[key] as number) : '—';
  $('#analyzed-coverage').innerHTML = `${count('analyzed')} <span>/ 6,236</span>`;
  $('#detected-coverage').innerHTML = `${count('detected')} <span>/ 6,236</span>`;
} else {
  $('#analyzed-coverage').textContent = 'Pass pending';
  $('#detected-coverage').textContent = 'Pass pending';
}
if (Object.keys(morphology).length) $('#morphology-notice').innerHTML += ' Morphology: <a href="https://corpus.quran.com" target="_blank" rel="noreferrer">Quranic Arabic Corpus 0.4</a> (original source notices), joined only where token alignment passes. Grammatical features never supply speaker identities. Unaligned words and conflicting fields remain unannotated.';
