#!/usr/bin/env node
/**
 * Offline ACSP/0.1 reference-TOK proposal preparation.
 * Contract: NetGovComEduGovOrgEduGovComNet@9fcf2e1, plus the inspected live
 * /protocol.json schemas archived in evidence/acsp-discovery.json.
 * This module contains no network transport and never reports server acceptance.
 */
import { readFile, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const SESSION = /^[A-Za-z0-9._:@-]{1,128}$/;
const IDEMPOTENCY = /^[A-Za-z0-9._:-]{8,128}$/;
const CONFIDENCE = ['unclassified', 'low', 'medium', 'high'];
const TYPES = ['observation', 'finding', 'hypothesis', 'question', 'constraint', 'decision', 'rejection', 'uncertainty', 'reference', 'task', 'delegation', 'closure'];
const isObject = (x) => x !== null && typeof x === 'object' && !Array.isArray(x);

function checkJson(value, path = 'analysis', parents = new Set()) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return;
  if (typeof value === 'number' && Number.isFinite(value)) return;
  if (typeof value !== 'object') throw new TypeError(`${path} must contain only finite JSON values`);
  if (parents.has(value)) throw new TypeError(`${path} contains a JSON cycle`);
  if (!Array.isArray(value) && Object.getPrototypeOf(value) !== Object.prototype && Object.getPrototypeOf(value) !== null) {
    throw new TypeError(`${path} must contain plain JSON objects`);
  }
  for (const key of Reflect.ownKeys(value)) {
    if (Array.isArray(value) && key === 'length') continue;
    const descriptor = Object.getOwnPropertyDescriptor(value, key);
    if (typeof key !== 'string' || !descriptor.enumerable || !('value' in descriptor)
        || (Array.isArray(value) && (!/^(0|[1-9]\d*)$/.test(key) || Number(key) >= value.length))) {
      throw new TypeError(`${path} contains properties that JSON would omit or execute`);
    }
  }
  parents.add(value);
  if (Array.isArray(value)) {
    for (let i = 0; i < value.length; i++) checkJson(value[i], `${path}[${i}]`, parents);
  } else {
    for (const [key, child] of Object.entries(value)) checkJson(child, `${path}.${key}`, parents);
  }
  parents.delete(value);
}

/** Return issues for the local credential-free propose-append subset of ACSP/0.1. */
export function validateAcspProposal(request) {
  const issues = [];
  const issue = (path, text) => issues.push(`${path}: ${text}`);
  const object = (value, path, allowed) => {
    if (!isObject(value)) { issue(path, 'must be an object'); return false; }
    for (const key of Object.keys(value)) if (!allowed.includes(key)) issue(`${path}.${key}`, 'unsupported property in offline export');
    return true;
  };
  const string = (value, path, max, min = 0) => {
    if (typeof value !== 'string' || value.length < min || value.length > max) issue(path, `must be a string of ${min}–${max} characters`);
  };
  try { checkJson(request, 'request'); }
  catch (error) { return [error.message]; }
  if (!object(request, 'request', ['protocol', 'operation', 'actor', 'expected_version', 'idempotency_key', 'payload'])) return issues;
  if (request.protocol !== 'ACSP/0.1') issue('protocol', 'must be ACSP/0.1');
  if (request.operation !== 'propose') issue('operation', 'offline adapter prepares propose only');
  if (typeof request.idempotency_key !== 'string' || !IDEMPOTENCY.test(request.idempotency_key)) issue('idempotency_key', 'must match [A-Za-z0-9._:-]{8,128}');
  if (request.expected_version !== undefined && (!Number.isInteger(request.expected_version) || request.expected_version < 1)) issue('expected_version', 'must be a positive integer');
  if (object(request.actor, 'actor', ['session_id', 'agent_id', 'kind'])) {
    if (typeof request.actor.session_id !== 'string' || !SESSION.test(request.actor.session_id)) issue('actor.session_id', 'must be an explicit valid session identifier');
    if (request.actor.agent_id !== undefined && (typeof request.actor.agent_id !== 'string' || !SESSION.test(request.actor.agent_id))) issue('actor.agent_id', 'must be a valid identifier');
    if (!['agent', 'human', 'system'].includes(request.actor.kind)) issue('actor.kind', 'must be agent, human or system');
  }
  if (object(request.payload, 'payload', ['operation', 'payload', 'rationale'])) {
    if (request.payload.operation !== 'append') issue('payload.operation', 'must be append');
    if (request.payload.rationale !== undefined) string(request.payload.rationale, 'payload.rationale', 5_000);
    const tok = request.payload.payload;
    if (object(tok, 'payload.payload', ['type', 'title', 'summary', 'content', 'stated_confidence', 'refs'])) {
      if (!TYPES.includes(tok.type)) issue('payload.payload.type', 'must be an actual ACSP TOK type');
      string(tok.title, 'payload.payload.title', 200, 1);
      if (typeof tok.title === 'string' && !tok.title.trim()) issue('payload.payload.title', 'must not be blank');
      if (tok.summary !== undefined) string(tok.summary, 'payload.payload.summary', 2_000);
      if (tok.content !== undefined) string(tok.content, 'payload.payload.content', 20_000);
      if (tok.stated_confidence !== undefined && !CONFIDENCE.includes(tok.stated_confidence)) issue('payload.payload.stated_confidence', 'must be unclassified, low, medium or high');
      if (!Array.isArray(tok.refs) || tok.refs.length < 1 || tok.refs.length > 20) issue('payload.payload.refs', 'must contain 1–20 source references for this export');
      else tok.refs.forEach((ref, index) => {
        const path = `payload.payload.refs[${index}]`;
        if (!isObject(ref)) { issue(path, 'must be a reference object'); return; }
        const kinds = ['tok', 'url', 'citation'].filter((key) => key in ref);
        if (kinds.length !== 1) { issue(path, 'must contain exactly one of tok, url or citation'); return; }
        const kind = kinds[0];
        object(ref, path, kind === 'citation' ? ['citation'] : [kind, 'note']);
        if (ref.note !== undefined) string(ref.note, `${path}.note`, 500);
        if (kind === 'citation') string(ref.citation, `${path}.citation`, 1_000, 1);
        if (kind === 'tok' && (typeof ref.tok !== 'string' || !/^TOK-\d{3,}$/.test(ref.tok))) issue(`${path}.tok`, 'must match TOK-001');
        if (kind === 'url') {
          string(ref.url, `${path}.url`, 2_000);
          try { if (!['http:', 'https:'].includes(new URL(ref.url).protocol)) throw new Error(); }
          catch { issue(`${path}.url`, 'must be an HTTP(S) source URL'); }
        }
      });
    }
  }
  if (Buffer.byteLength(JSON.stringify(request), 'utf8') > 65_536) issue('request', 'exceeds 65,536 UTF-8 bytes');
  return issues;
}

/**
 * Build a deterministic snapshot. Analysis is caller-supplied opaque JSON;
 * this adapter adds no scientific interpretation, confidence or lifecycle events.
 * Required: sessionId, idempotencyKey, title, summary, objective, analysis, refs.
 */
export function buildAcspProposal(input) {
  if (!isObject(input)) throw new TypeError('ACSP export input must be an object');
  if (typeof input.summary !== 'string') throw new TypeError('summary must be supplied explicitly');
  if (typeof input.objective !== 'string' || !input.objective.trim()) throw new TypeError('objective must be supplied explicitly');
  checkJson(input.analysis);
  checkJson(input.refs, 'references');
  const request = {
    protocol: 'ACSP/0.1',
    operation: 'propose',
    actor: { session_id: input.sessionId, kind: 'agent' },
    ...(input.expectedVersion !== undefined ? { expected_version: input.expectedVersion } : {}),
    idempotency_key: input.idempotencyKey,
    payload: {
      operation: 'append',
      payload: {
        type: 'reference', title: input.title, summary: input.summary,
        content: JSON.stringify({ schemaVersion: 'snad.acsp-artifact.v1', objective: input.objective, analysis: input.analysis }),
        stated_confidence: 'unclassified', refs: structuredClone(input.refs),
      },
      rationale: 'Prepared locally as a source-bound SNAD artifact for owner review; no request has been sent.',
    },
  };
  const issues = validateAcspProposal(request);
  if (issues.length) throw new TypeError(`Invalid offline ACSP proposal: ${issues.join('; ')}`);
  return request;
}

async function main(args) {
  if (args.length < 2 || args[0] !== '--input' || (args.length !== 2 && (args.length !== 4 || args[2] !== '--output'))) {
    throw new Error('Usage: node scripts/integrations/acsp.mjs --input analysis-export.json [--output proposal.json]');
  }
  const request = buildAcspProposal(JSON.parse(await readFile(args[1], 'utf8')));
  const json = JSON.stringify(request, null, 2) + '\n';
  if (args[2] === '--output') await writeFile(args[3], json);
  else process.stdout.write(json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main(process.argv.slice(2)).catch((error) => { process.stderr.write(`${error.message}\n`); process.exitCode = 1; });
}
