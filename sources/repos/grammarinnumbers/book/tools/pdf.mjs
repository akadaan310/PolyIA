// Assemble the research ledger into one academic PDF textbook (Chromium print).
import fs from "node:fs"; import path from "node:path"; import MarkdownIt from "markdown-it"; import { chromium } from "playwright-core";
const R = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const md = new MarkdownIt({ html: false, typographer: true });
const parts = [["I. Charter and Provenance", ["RESEARCH_CHARTER.md", "PROVENANCE.md"]],
 ["II. The Grammar of Number", ["NUMBER_GRAMMAR.md", "DEFINITIONS.md"]],
 ["III. Arithmetic, Zero and Admissibility", ["ARITHMETIC_GRAMMAR.md", "RESULTS.md"]],
 ["IV. Machines", ["MACHINE_MODEL.md", "FORMAL_MODELS.md"]],
 ["V. Number Theory", ["NUMBER_THEORY.md"]],
 ["VI. Evidence", ["EXPERIMENTS.md", "experiments/results/SUMMARY.md", "HYPOTHESES.md", "COUNTEREXAMPLES.md"]],
 ["VII. CGT and the Frontier", ["CGT_CONCEPT_MAP.md", "OPEN_PROBLEMS.md", "LITERATURE_REVIEW.md", "BOOK_OUTLINE.md", "DECISION_LOG.md"]]];
const bib = JSON.parse(fs.readFileSync(path.join(R, "book/content/bibliography.json"), "utf8"));
let toc = "", body = "", n = 0;
for (const [pt, files] of parts) {
  body += `<h1 class="part">${pt}</h1>`; toc += `<li class="tp">${pt}</li>`;
  for (const f of files) { n++; const src = fs.readFileSync(path.join(R, f), "utf8");
    const title = (src.match(/^#\s+(.*)$/m) || [, f])[1];
    toc += `<li>Chapter ${n}. ${md.renderInline(title)}</li>`;
    body += `<section class="ch"><p class="chn">Chapter ${n}</p>${md.render(src.replace(/^#\s+/m, "# "))}</section>`; } }
const refs = Object.values(bib).sort((a, b) => a.label.localeCompare(b.label)).map(b => `<li><b>${b.label}</b>. ${b.authors} (${b.year}). <i>${b.title}</i>. ${b.venue}. <span class="v">[${b.verification}]</span></li>`).join("");
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@page{size:A4;margin:22mm 20mm}body{font:10.5pt/1.5 "DejaVu Serif",Georgia,serif;color:#1c1e21}
h1{font-size:20pt;color:#1d3a8a;page-break-before:always;border-bottom:2px solid #1d3a8a}h1.part{font-size:26pt;text-align:center;margin-top:35%;border:0}
h2{font-size:14pt;color:#1d3a8a;margin-top:1.4em}h3{font-size:12pt}.chn{page-break-before:always;color:#8a6d2f;font-variant:small-caps;letter-spacing:.1em;margin:0}.ch h1{page-break-before:avoid}
table{border-collapse:collapse;font-size:8.3pt;width:100%;margin:.8em 0}td,th{border:1px solid #bbb;padding:2px 4px;vertical-align:top}th{background:#eef1f8}
code,pre{font:8.5pt "DejaVu Sans Mono",monospace;background:#f3f1ea}pre{padding:6px;white-space:pre-wrap}blockquote{border-left:3px solid #8a6d2f;margin-left:0;padding-left:10px;color:#3c4045}
.title{text-align:center;padding-top:30%}.title h1{border:0;font-size:34pt;page-break-before:avoid}.toc li{list-style:none}.tp{font-weight:bold;margin-top:.6em}.v{color:#777;font-size:8pt}</style></head><body>
<div class="title"><h1>Grammar in Numbers</h1><p style="font-size:15pt">Arithmetic, Number Theory, and the Computational Grammar of Number</p>
<p style="margin-top:3em;font-size:13pt"><b>Abed Kadaan</b><br>Founding Principal Researcher</p><p>A frontier volume of the Computational Grammar Theory research program<br>Working edition 0.1 · October 2026</p>
<p style="margin-top:4em;font-size:9pt;color:#555">Research manuscript, not peer reviewed. Results marked “proved here” are self-checked and exhaustively verified on small cases by the accompanying code; nearly all are classical or elementary. Code, data and reproduction: github.com/akadaan310/grammarinnumbers</p></div>
<h1>Contents</h1><ul class="toc">${toc}<li class="tp">Bibliography</li></ul>${body}<h1>Bibliography</h1><ol>${refs}</ol></body></html>`;
fs.writeFileSync(path.join(R, "book/grammar-in-numbers.html"), html);
const br = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" in process.env ? undefined : undefined });
const pg = await br.newPage(); await pg.setContent(html, { waitUntil: "load" });
await pg.pdf({ path: path.join(R, "Grammar-in-Numbers.pdf"), format: "A4", printBackground: true, displayHeaderFooter: true,
  headerTemplate: "<span></span>", footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#666">Grammar in Numbers — A. Kadaan · <span class="pageNumber"></span></div>', margin: { top: "20mm", bottom: "20mm", left: "18mm", right: "18mm" } });
await br.close(); console.log("ok");
