import { CommandClient, ProtocolError } from './client.mjs';

const client = new CommandClient();
const $ = id => document.getElementById(id);
const json = value => JSON.stringify(value, null, 2);
let session = 0;
let live = false;
let working = false;
let refreshing = null;
let renderedHead = null;
let eventCursor = 0;
let loadedEvents = [];
let loadingEvents = false;
let selectedArtifact = null;
let artifactRequirement = null;
let artifactChunk = null;
let artifactRequest = 0;
let loadingArtifact = false;

function node(tag, text = '', className = '') {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  return element;
}

function badge(status) {
  const color = ['ACCEPTED', 'APPLIED', 'PASS'].includes(status) ? 'green'
    : ['VERIFIED', 'ACKNOWLEDGED'].includes(status) ? 'blue'
    : ['PRODUCED', 'SUBMITTED', 'DEFERRED', 'PAUSED'].includes(status) ? 'amber'
    : ['REJECTED', 'FAIL', 'ERROR', 'REFUSED'].includes(status) ? 'red' : 'neutral';
  return node('span', status || 'UNKNOWN', 'badge badge-' + color);
}

function options(select, choices, emptyText) {
  const previous = select.value;
  const items = choices.map(([value, title]) => {
    const option = node('option', title);
    option.value = value;
    return option;
  });
  if (!items.length) { const empty = node('option', emptyText); empty.value = ''; items.push(empty); }
  select.replaceChildren(...items);
  if (choices.some(([value]) => value === previous)) select.value = previous;
}

function connection(label, mode = '') {
  $('connection-label').textContent = label;
  $('connection-status').className = 'connection-status' + (mode ? ' ' + mode : '');
}

function clearMessage() {
  $('error-banner').hidden = true;
  $('notice').hidden = true;
}

function showError(error) {
  if (error.code === 'SESSION_CHANGED') return;
  $('notice').hidden = true;
  $('error-title').textContent = error.code || 'REQUEST_ERROR';
  let message = error.message || 'The request could not be completed.';
  if (error.code === 'REVISION_CONFLICT') message += ' State has been refreshed. Review it, then submit your intended command again.';
  if (error.requestId) message += ' Request reference: ' + error.requestId + '.';
  $('error-message').textContent = message;
  $('error-details').textContent = error.details ? json(error.details) : '';
  $('error-details').hidden = !error.details;
  $('error-banner').hidden = false;
}

function notice(message) {
  $('notice').textContent = message;
  $('notice').hidden = false;
}

function canCommand() {
  return client.connected && live && client.scope === 'operator' && !working && !client.hasPending;
}

function updateControls() {
  const read = client.connected;
  const command = canCommand();
  document.querySelectorAll('[data-read]').forEach(element => { element.disabled = !read; });
  document.querySelectorAll('[data-command], [data-command-input]').forEach(element => { element.disabled = !command; });
  $('disconnect-button').disabled = !read && !working;
  const requirement = client.state?.requirements[$('requirement-select').value];
  $('verify-requirement').disabled = !command || !requirement?.artifacts?.length;
  $('accept-requirement').disabled = !command || requirement?.status !== 'VERIFIED';
  const guidance = client.state?.guidance[$('guidance-select').value];
  $('apply-guidance').disabled = !command || guidance?.status !== 'ACKNOWLEDGED' || !guidance.action;
  const closed = !guidance || ['APPLIED', 'REJECTED'].includes(guidance.status);
  $('ack-form').querySelector('button[type="submit"]').disabled = !command || closed;
  $('guidance-disposition').disabled = !command || closed;
  $('guidance-reason').disabled = !command || closed;
  $('run-experiment').disabled = !command || Boolean(client.state?.research?.paused);
  $('run-intake').disabled = !command || Boolean(client.state?.research?.paused);
  $('load-checkpoint').disabled = !read || !client.state?.latest_checkpoint;
  $('artifact-load').disabled = !read || !selectedArtifact || loadingArtifact;
  $('artifact-next').disabled = !read || !selectedArtifact || loadingArtifact || artifactChunk?.next_offset == null;
  $('retry-panel').hidden = !client.hasPending;
  $('retry-command').disabled = working || !read || client.scope !== 'operator';
  $('retry-text').textContent = client.hasPending
    ? 'The result of ' + client.pendingId + ' is unresolved. Recover its receipt with the exact same request.' : '';
}

function renderRequirements() {
  const query = $('requirement-search').value.toLowerCase().trim();
  const status = $('requirement-filter').value;
  const requirements = Object.values(client.state?.requirements || {});
  const filtered = requirements.filter(item => (!status || item.status === status)
    && (!query || [item.id, item.title, item.verifier].join(' ').toLowerCase().includes(query)));
  const rows = filtered.map(item => {
    const row = document.createElement('tr');
    const title = document.createElement('td');
    title.append(node('span', item.id, 'requirement-id'), node('div', item.title, 'requirement-title'));
    const state = document.createElement('td'); state.append(badge(item.status));
    const priority = node('td', String(item.priority), 'mono');
    const action = document.createElement('td');
    const inspect = node('button', '↗', 'table-button');
    inspect.type = 'button'; inspect.setAttribute('aria-label', 'Inspect ' + item.id);
    inspect.addEventListener('click', () => { $('requirement-select').value = item.id; renderSelectedRequirement(); $('requirement-select').focus(); });
    action.append(inspect); row.append(title, state, priority, action); return row;
  });
  if (!rows.length) {
    const row = document.createElement('tr');
    const cell = node('td', client.state ? 'No obligations match this filter.' : 'Connect to view the constitution’s obligations.', 'empty-cell');
    cell.colSpan = 4; row.append(cell); rows.push(row);
  }
  $('requirements-body').replaceChildren(...rows);
  $('requirements-caption').textContent = client.state ? filtered.length + ' of ' + requirements.length + ' obligations shown' : 'No obligations loaded';
}

function renderSelectedRequirement() {
  const requirement = client.state?.requirements[$('requirement-select').value];
  $('selected-requirement-title').textContent = requirement?.title || 'Select an obligation to inspect its evidence.';
  $('selected-requirement-meta').textContent = requirement
    ? requirement.status + ' · Verifier: ' + requirement.verifier + ' · Priority ' + requirement.priority : '';
  $('requirement-detail').textContent = requirement ? json(requirement) : 'No obligation selected.';
  renderArtifacts(requirement);
  updateControls();
}

function clearArtifact() {
  artifactRequest += 1;
  selectedArtifact = null; artifactChunk = null; loadingArtifact = false;
  $('artifact-panel').hidden = true;
  $('artifact-identity').textContent = ''; $('artifact-status').textContent = '';
  $('artifact-output').textContent = '';
}

function renderArtifacts(requirement) {
  const artifacts = requirement?.artifacts || [];
  if (artifactRequirement !== requirement?.id || selectedArtifact &&
      !artifacts.some(item => item.sha256 === selectedArtifact.sha256 && item.path === selectedArtifact.path)) clearArtifact();
  artifactRequirement = requirement?.id;
  const items = artifacts.map(artifact => {
    const item = node('li');
    const inspect = node('button', 'Inspect bytes'); inspect.type = 'button';
    inspect.setAttribute('data-read', '');
    inspect.setAttribute('aria-label', 'Inspect captured bytes of ' + artifact.path);
    inspect.addEventListener('click', () => {
      clearArtifact(); selectedArtifact = artifact;
      $('artifact-panel').hidden = false;
      $('artifact-identity').textContent = artifact.path + ' · SHA-256 ' + artifact.sha256;
      $('artifact-offset').value = '0'; $('artifact-limit').value = '65536';
      $('artifact-encoding').value = 'utf8';
      loadArtifactChunk();
    });
    item.append(node('strong', artifact.path), node('p', artifact.size + ' bytes · ' + artifact.sha256, 'mono small'), inspect);
    return item;
  });
  $('captured-artifacts').replaceChildren(...(items.length ? items : [node('li', 'No captured artifacts for this obligation.', 'muted')]));
}

function renderArtifactChunk() {
  if (!artifactChunk) return;
  const chunk = artifactChunk;
  const partial = chunk.offset !== 0 || chunk.next_offset !== null;
  const textView = $('artifact-encoding').value === 'utf8' && chunk.text !== null;
  $('artifact-status').textContent = (partial ? 'Partial' : 'Complete') + ' captured object · bytes [' + chunk.offset + ', '
    + (chunk.offset + chunk.byteLength) + ') of ' + chunk.total_size + '. '
    + (chunk.text === null ? 'Binary or incomplete UTF-8 sequence. ' : '')
    + (textView ? 'UTF-8 text view.' : 'Exact bytes shown as base64.');
  $('artifact-output').textContent = textView ? chunk.text : chunk.data;
  updateControls();
}

async function loadArtifactChunk() {
  if (!client.connected || !selectedArtifact || loadingArtifact) return;
  const epoch = session, request = ++artifactRequest, artifact = selectedArtifact;
  clearMessage(); artifactChunk = null; $('artifact-output').textContent = '';
  loadingArtifact = true; $('artifact-status').textContent = 'Reading captured bytes…'; updateControls();
  try {
    const offset = Number($('artifact-offset').value), limit = Number($('artifact-limit').value);
    if (!/^[0-9]+$/.test($('artifact-offset').value) || !Number.isSafeInteger(offset) || offset > artifact.size ||
        !/^[0-9]+$/.test($('artifact-limit').value) || !Number.isSafeInteger(limit) || limit < 1 || limit > 65536) {
      throw new ProtocolError('INVALID_RANGE', 'Use a byte offset within the captured object and a chunk size from 1 to 65,536.');
    }
    const chunk = await client.read('/v1/blobs/' + artifact.sha256 + '?offset=' + offset + '&limit=' + limit);
    if (epoch !== session || request !== artifactRequest) return;
    if (chunk?.digest !== artifact.sha256 || chunk.total_size !== artifact.size || chunk.offset !== offset ||
        chunk.encoding !== 'base64' || typeof chunk.data !== 'string' || chunk.data.length > 87384 ||
        !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(chunk.data)) {
      throw new ProtocolError('INVALID_RESPONSE', 'The artifact response does not match the selected capture.');
    }
    const binary = atob(chunk.data);
    const expectedLength = Math.min(limit, artifact.size - offset);
    const next = offset + expectedLength < artifact.size ? offset + expectedLength : null;
    if (binary.length !== expectedLength || btoa(binary) !== chunk.data || chunk.next_offset !== next) {
      throw new ProtocolError('INVALID_RESPONSE', 'The artifact response has an invalid byte length or continuation.');
    }
    let text = null;
    try {
      text = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(Uint8Array.from(binary, char => char.charCodeAt(0)));
      if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(text)) text = null;
    } catch (_) { /* Keep exact base64 when a chunk is binary or splits UTF-8. */ }
    artifactChunk = { ...chunk, text, byteLength: binary.length };
    renderArtifactChunk();
  } catch (error) {
    if (epoch === session && request === artifactRequest) {
      $('artifact-status').textContent = 'No chunk loaded.'; showError(error);
    }
  } finally {
    if (epoch === session && request === artifactRequest) { loadingArtifact = false; updateControls(); }
  }
}

function renderSelectedGuidance() {
  const guidance = client.state?.guidance[$('guidance-select').value];
  const preview = $('guidance-preview');
  if (!guidance) {
    preview.replaceChildren(node('p', 'Submitted text and its registered action appear here.', 'muted'));
    $('guidance-detail').textContent = 'No guidance selected.';
    $('guidance-apply-help').textContent = 'Apply becomes available for acknowledged guidance with a registered action.';
  } else {
    preview.replaceChildren(badge(guidance.status), node('p', guidance.text),
      node('p', guidance.action ? 'Action: ' + JSON.stringify(guidance.action) : 'Text only · no executable action', 'mono'));
    $('guidance-detail').textContent = json(guidance);
    $('guidance-apply-help').textContent = guidance.status === 'APPLIED'
      ? 'Applied at revision ' + guidance.applied_revision + '. Exact effects are retained in the record.'
      : !guidance.action ? 'This guidance records text only. It cannot be labelled applied.'
      : guidance.status === 'ACKNOWLEDGED' ? 'Acknowledged. Applying will execute only the registered action shown above.'
      : 'Record an acknowledgment before applying the registered action.';
  }
  updateControls();
}

function renderRuns() {
  const runs = client.state?.runs || [];
  $('run-total').textContent = client.state ? runs.length + ' recorded' : '0 loaded';
  const list = runs.slice(-20).reverse().map(run => {
    const article = node('article', '', 'record-item');
    const top = node('div', '', 'record-top');
    top.append(node('strong', run.name), badge(run.report?.status));
    const caption = node('p', 'Revision ' + run.revision + ' · ' + (run.report?.evidence_class || 'No evidence class'), 'mono');
    const detail = document.createElement('details');
    detail.append(node('summary', 'Inputs, checks, code identity & limitations'), node('pre', json(run)));
    article.append(top, caption, detail); return article;
  });
  if (!list.length) list.push(node('p', client.state ? 'No experiments have been recorded.' : 'Connect to view recorded experiments and their limitations.', 'empty-state'));
  $('runs-list').replaceChildren(...list);
}

function renderIntake() {
  const run = [...(client.state?.runs || [])].reverse().find(item => item.name === 'intake');
  const panel = $('intake-result');
  if (!run) {
    panel.replaceChildren(node('p', client.state ? 'No intake has been recorded.' : 'Connect to inspect a recorded intake.', 'empty-state'));
    return;
  }
  const report = run.report, result = report.result;
  const content = [badge(report.status), node('p', 'Revision ' + run.revision + ' · ' + report.evidence_class, 'mono')];
  if (result.source) {
    content.push(node('p', 'Source ' + result.source.sha256, 'mono'));
    for (const item of result.interpretations) {
      content.push(node('h4', item.kind), node('p', item.explanation));
    }
    for (const unknown of result.unresolved) content.push(node('p', unknown.reason + ': ' + unknown.detail));
    if (result.opportunities.length) content.push(node('p', result.opportunities.length + ' research proposals retained; no automatic execution.'));
  } else content.push(node('p', result.detail || result.reason || 'No interpretation admitted.'));
  const detail = document.createElement('details');
  detail.append(node('summary', 'Original source, spans, outputs & evidence'), node('pre', json(run)));
  content.push(detail);
  panel.replaceChildren(...content);
}

function renderState(force = false) {
  const state = client.state;
  if (!state) { renderDisconnected(); return; }
  $('revision').textContent = String(state.revision);
  $('head-short').textContent = 'head ' + state.head.slice(0, 15) + '…';
  $('head-short').title = state.head;
  $('mission-status').textContent = state.commission_status === 'NOT_COMMISSIONED' ? 'Not commissioned' : state.commission_status;
  const requirements = Object.values(state.requirements);
  const guidance = Object.values(state.guidance);
  const accepted = requirements.filter(item => item.status === 'ACCEPTED').length;
  $('accepted-count').textContent = String(accepted);
  $('requirement-total').textContent = '/ ' + requirements.length;
  $('acceptance-progress').max = Math.max(1, requirements.length);
  $('acceptance-progress').value = accepted;
  $('acceptance-caption').textContent = accepted + ' accepted · scoped evidence';
  $('pending-guidance').textContent = String(guidance.filter(item => ['SUBMITTED', 'DEFERRED'].includes(item.status)).length);
  $('guidance-caption').textContent = guidance.length + ' recorded · ' + guidance.filter(item => item.status === 'APPLIED').length + ' applied';
  $('research-state').textContent = state.research.paused ? 'Paused' : 'Active';
  $('research-badge').textContent = state.research.paused ? 'Paused by guidance' : 'Available';
  $('research-badge').className = 'badge ' + (state.research.paused ? 'badge-amber' : 'badge-green');
  $('runs-count').textContent = state.runs.length + ' recorded scientific runs';
  $('latest-checkpoint').textContent = state.latest_checkpoint
    ? state.latest_checkpoint.id + ' · revision ' + state.latest_checkpoint.revision + (state.latest_checkpoint.note ? ' · ' + state.latest_checkpoint.note : '')
    : 'No checkpoint has been created.';
  $('scope-display').textContent = client.scope === 'operator' ? 'Operator · reads + commands' : 'Read access only';
  $('session-description').textContent = client.scope === 'operator'
    ? 'Operator connected. Commands record the current revision and return a receipt.'
    : 'Read access connected. State, evidence, receipts, and verification are available.';
  if (force || renderedHead !== state.head) {
    options($('requirement-select'), requirements.map(item => [item.id, item.id + ' · ' + item.title]), 'No obligations');
    options($('guidance-target'), [['research', 'Research program'], ...requirements.map(item => [item.id, item.id + ' · ' + item.title])], 'No targets');
    options($('guidance-select'), guidance.sort((a, b) => b.submitted_revision - a.submitted_revision)
      .map(item => [item.id, item.status + ' · ' + item.target + ' · ' + item.text.slice(0, 60)]), 'No guidance recorded');
    $('guidance-queue-count').textContent = guidance.length + ' recorded';
    renderRequirements(); renderSelectedRequirement(); renderSelectedGuidance(); renderRuns(); renderIntake();
    renderedHead = state.head;
  }
  updateControls();
}

function renderDisconnected() {
  clearArtifact(); artifactRequirement = null;
  renderedHead = null; loadedEvents = []; eventCursor = 0;
  ['revision', 'accepted-count', 'pending-guidance', 'research-state'].forEach(id => { $(id).textContent = '—'; });
  $('head-short').textContent = 'Connect to read state'; $('head-short').removeAttribute('title');
  $('requirement-total').textContent = ''; $('acceptance-progress').value = 0;
  $('acceptance-caption').textContent = 'Awaiting ledger state';
  $('guidance-caption').textContent = 'Submit · acknowledge · apply';
  $('runs-count').textContent = 'Registered exact functions only';
  $('last-refresh').textContent = 'No state received'; $('scope-display').textContent = 'No access scope';
  $('session-description').textContent = 'Enter an operator or read token. It stays in this tab’s memory.';
  $('research-badge').textContent = 'Awaiting state'; $('research-badge').className = 'badge badge-neutral';
  $('latest-checkpoint').textContent = 'No snapshot loaded.';
  $('verification-status').textContent = 'No verification requested in this session.';
  $('guidance-queue-count').textContent = 'No guidance';
  options($('requirement-select'), [], 'Connect first');
  options($('guidance-target'), [['research', 'Research program']], 'Connect first');
  options($('guidance-select'), [], 'No guidance recorded');
  for (const id of ['receipt-output', 'checkpoint-output', 'verification-output', 'refusals-output', 'event-output']) $(id).textContent = 'No record loaded in this session.';
  $('receipt-id').value = '';
  renderRequirements(); renderSelectedRequirement(); renderSelectedGuidance(); renderRuns(); renderIntake(); renderEvents(); updateControls();
}

function renderEvents() {
  const rows = loadedEvents.slice().reverse().map(event => {
    const row = document.createElement('tr');
    const action = document.createElement('td');
    const inspect = node('button', '↗', 'table-button'); inspect.type = 'button';
    inspect.setAttribute('aria-label', 'Inspect event at revision ' + event.sequence);
    inspect.addEventListener('click', () => { $('event-output').textContent = json(event); $('event-details').open = true; });
    action.append(inspect);
    row.append(node('td', '#' + event.sequence, 'mono'), node('td', event.kind, 'mono'),
      node('td', event.actor), node('td', new Date(event.timestamp).toLocaleString(), 'mono'), action);
    return row;
  });
  if (!rows.length) {
    const row = document.createElement('tr');
    const cell = node('td', client.state ? 'No committed events loaded.' : 'Committed events appear after connection. Refusals are separate.', 'empty-cell');
    cell.colSpan = 5; row.append(cell); rows.push(row);
  }
  $('events-body').replaceChildren(...rows);
  $('event-cursor').textContent = client.state ? 'Cursor ' + eventCursor + ' · state revision ' + client.state.revision : 'Cursor —';
}

async function loadEvents() {
  if (!client.connected || loadingEvents) return;
  loadingEvents = true;
  const epoch = session;
  try {
    const feed = await client.read('/v1/events?after=' + eventCursor + '&limit=100');
    if (epoch !== session) return;
    if (!Array.isArray(feed.events) || !Number.isInteger(feed.next_after)) throw new ProtocolError('INVALID_RESPONSE', 'The event feed returned an invalid cursor.');
    loadedEvents = [...loadedEvents, ...feed.events].slice(-100);
    eventCursor = feed.next_after;
    renderEvents();
  } finally { loadingEvents = false; }
}

async function sync() {
  if (!client.connected) return;
  if (refreshing) return refreshing;
  const epoch = session;
  refreshing = (async () => {
    try {
      const previous = client.state;
      await client.refresh();
      if (epoch !== session) return;
      if (previous && client.state.revision < previous.revision) {
        loadedEvents = []; eventCursor = 0;
        notice('The service is reporting an earlier revision. Event polling restarted from the beginning; inspect the ledger before issuing commands.');
      }
      live = true; connection(document.hidden ? 'Connected · polling paused' : 'Connected · live', 'connected');
      renderState();
      $('last-refresh').textContent = 'State received ' + new Date().toLocaleTimeString();
      await loadEvents();
    } catch (error) {
      if (epoch !== session) return;
      live = false; connection('Connection needs attention', 'stale'); updateControls(); showError(error);
    } finally { if (epoch === session) refreshing = null; }
  })();
  return refreshing;
}

async function runRead(path, target, detail, label) {
  const epoch = session;
  clearMessage();
  try {
    const result = await client.read(path);
    if (epoch !== session) return;
    $(target).textContent = json(result); $(detail).open = true;
    if (label === 'verification') {
      $('verification-status').textContent = result.ok ? 'Verification passed for the checked ledger, artifacts, and checkpoints.' : 'Verification found a problem. Inspect the diagnostics; no repair was applied.';
      if (!result.ok) showError(new ProtocolError('INTEGRITY_FAILURE', 'Ledger verification reported a failure.', 200, result));
    }
  } catch (error) { if (epoch === session) showError(error); }
}

async function execute(kind, payload, retry = false) {
  if (working) return;
  const epoch = session;
  clearMessage(); working = true; updateControls();
  try {
    const receipt = retry ? await client.retry() : await client.command(kind, payload);
    if (epoch !== session) return;
    $('receipt-output').textContent = json(receipt); $('receipt-details').open = true;
    $('receipt-id').value = receipt.command_id;
    let outcome = '';
    if (receipt.result?.verification) outcome = ' Verifier outcome: ' + receipt.result.verification.outcome + '.';
    if (receipt.result?.run) outcome = ' Scientific result: ' + receipt.result.run.report.status + '. Inspect its evidence class and limitations.';
    notice('Command recorded at revision ' + receipt.revision + '. Receipt: ' + receipt.command_id + '.' + outcome);
  } catch (error) {
    if (epoch === session) showError(error);
  } finally {
    if (epoch === session) {
      working = false;
      if (refreshing) await refreshing;
      await sync(); updateControls();
    }
  }
}

function form(id, handler) {
  $(id).addEventListener('submit', event => {
    event.preventDefault();
    Promise.resolve().then(handler).catch(showError);
  });
}

form('connect-form', async () => {
  const token = $('token').value; $('token').value = '';
  const epoch = ++session;
  clearArtifact();
  clearMessage(); live = false; working = false; renderedHead = null; refreshing = null; loadingEvents = false;
  loadedEvents = []; eventCursor = 0;
  $('connect-button').disabled = true; connection('Connecting…');
  try {
    await client.connect(token);
    if (epoch !== session) return;
    live = true; renderState(true); connection('Connected · live', 'connected');
    $('last-refresh').textContent = 'State received ' + new Date().toLocaleTimeString();
    await loadEvents();
  } catch (error) {
    if (epoch === session) { live = false; connection('Disconnected'); renderDisconnected(); showError(error); }
  } finally {
    if (epoch === session) { $('connect-button').disabled = false; updateControls(); }
  }
});

$('disconnect-button').addEventListener('click', () => {
  session += 1; client.disconnect(); live = false; working = false; refreshing = null; loadingEvents = false;
  $('token').value = ''; $('connect-button').disabled = false; clearMessage(); connection('Disconnected'); renderDisconnected();
});
$('dismiss-error').addEventListener('click', () => { $('error-banner').hidden = true; });
$('refresh-button').addEventListener('click', () => { clearMessage(); sync(); });
$('requirement-search').addEventListener('input', renderRequirements);
$('requirement-filter').addEventListener('change', renderRequirements);
$('requirement-select').addEventListener('change', renderSelectedRequirement);
form('artifact-chunk-form', loadArtifactChunk);
$('artifact-encoding').addEventListener('change', renderArtifactChunk);
$('artifact-next').addEventListener('click', () => {
  if (artifactChunk?.next_offset == null) return;
  $('artifact-offset').value = String(artifactChunk.next_offset);
  loadArtifactChunk();
});
$('guidance-select').addEventListener('change', renderSelectedGuidance);
$('guidance-action').addEventListener('change', () => {
  const action = $('guidance-action').value;
  $('priority-field').hidden = action !== 'set_priority';
  if (['pause_research', 'resume_research'].includes(action)) $('guidance-target').value = 'research';
});

form('produce-form', () => execute('requirement.produce', {
  requirement_id: $('requirement-select').value,
  artifacts: $('artifact-paths').value.split(/\r?\n/).map(value => value.trim()).filter(Boolean), note: $('production-note').value,
}));
$('verify-requirement').addEventListener('click', () => execute('requirement.verify', { requirement_id: $('requirement-select').value }));
$('accept-requirement').addEventListener('click', () => execute('requirement.accept', { requirement_id: $('requirement-select').value }));
form('guidance-form', () => {
  const target = $('guidance-target').value;
  const payload = { target, text: $('guidance-text').value };
  const kind = $('guidance-action').value;
  if (kind === 'set_priority') {
    if (target === 'research') throw new ProtocolError('TARGET_REQUIRED', 'Choose an obligation target before setting its priority.');
    const priority = Number($('guidance-priority').value);
    if (!Number.isInteger(priority) || priority < 0 || priority > 9) throw new ProtocolError('INVALID_PRIORITY', 'Priority must be an integer from 0 through 9.');
    payload.action = { kind, target, priority };
  } else if (kind) {
    if (target !== 'research') throw new ProtocolError('TARGET_REQUIRED', 'Pause and resume actions require the research program target.');
    payload.action = { kind };
  }
  return execute('guidance.submit', payload);
});
form('ack-form', () => execute('guidance.ack', {
  guidance_id: $('guidance-select').value, disposition: $('guidance-disposition').value, reason: $('guidance-reason').value,
}));
$('apply-guidance').addEventListener('click', () => execute('guidance.apply', { guidance_id: $('guidance-select').value }));
form('experiment-form', () => {
  let parameters;
  try { parameters = JSON.parse($('experiment-parameters').value); } catch (_) {
    throw new ProtocolError('INVALID_PARAMETERS', 'Experiment parameters must be a valid JSON object.');
  }
  if (!parameters || typeof parameters !== 'object' || Array.isArray(parameters)) throw new ProtocolError('INVALID_PARAMETERS', 'Experiment parameters must be a JSON object.');
  return execute('experiment.run', { name: $('experiment-name').value, parameters });
});
function loadExperimentExample(name, parameters) {
  $('experiment-name').value = name;
  $('experiment-parameters').value = json(parameters);
  clearMessage(); notice('Example loaded. Review the parameters, then choose Run exact checks.');
}

const naturalAlphabetExample = {
  version: 'polyia.alphabet/0.1', entity_id: 'example:natural-numbers', kind: 'numeric',
  interpretation: 'Nonnegative integers queried individually; this example does not enumerate infinity.',
  sources: [{ source: 'GOD_SEED.md', anchor: 'PIA-050; Natural example is a declared construction',
    sha256: '4f179f83ff2279e1bf3e471ac8edc80456b9fdff29548332bf5b649a3c724f38' }],
  generator: { name: 'naturals', start: 0, coordinates: 'value' },
  group: { elements: [{ id: 'e', rule: 'identity' }] },
};

$('rasm-example').addEventListener('click', () => loadExperimentExample('rasm', {
  version: 'polyia.rasm/0.1', chart: 'timeless.rsa28/0.1', operation: 'project', text: 'كتب',
}));
$('generators-example').addEventListener('click', () => loadExperimentExample('generators', {
  card: {
    schema: 'polyia.generator-card/0.1', id: 'request-ack-protocol', version: '1.0.0', family: 'regular',
    alphabet: ['PING', 'ACK'], seed: 0,
    grammar: { op: 'sequence', parts: [{ op: 'token', token: 'PING' },
      { op: 'repeat', body: { op: 'token', token: 'ACK' }, min: 1, max: 2 }] },
    bounds: { work_units: 10000, max_candidates: 64 },
  },
  request: { operation: 'generate' }, style: 'tutorial',
}));
$('forms-natural-example').addEventListener('click', () => loadExperimentExample('forms', {
  version: 'polyia.forms/0.1', operation: 'generate', alphabet: naturalAlphabetExample, index: 7,
}));
$('forms-word-example').addEventListener('click', () => loadExperimentExample('forms', {
  version: 'polyia.forms/0.1', operation: 'serialize', alphabet: naturalAlphabetExample,
  word: {
    version: 'polyia.word/0.1', entity_id: 'example:ordered-pair',
    alphabet_cid: '14ada374b35da1fc96a7f057bc6793d88243fb75d9dc01c8908b317c8bf2a615',
    index: { kind: 'tuple', length: 2 }, labels: { '0': '0', '1': '7' },
  },
}));
form('intake-form', () => {
  const text = $('intake-text').value;
  if (!text.trim() || new TextEncoder().encode(text).byteLength > 16384) {
    throw new ProtocolError('INTAKE_LIMIT', 'Submit nonempty text of at most 16,384 UTF-8 bytes.');
  }
  return execute('experiment.run', { name: 'intake', parameters: {
    text, format: $('intake-format').value, style: $('intake-style').value,
  } });
});
form('checkpoint-form', () => execute('checkpoint.create', { note: $('checkpoint-note').value }));
$('load-checkpoint').addEventListener('click', () => runRead('/v1/checkpoints/latest', 'checkpoint-output', 'checkpoint-details'));
$('verify-ledger').addEventListener('click', () => runRead('/v1/verify', 'verification-output', 'verification-details', 'verification'));
form('receipt-form', () => runRead('/v1/commands/' + encodeURIComponent($('receipt-id').value.trim()), 'receipt-output', 'receipt-details'));
$('load-refusals').addEventListener('click', () => runRead('/v1/refusals?limit=25', 'refusals-output', 'refusals-details'));
$('load-events').addEventListener('click', () => loadEvents().catch(showError));
$('retry-command').addEventListener('click', () => execute(null, null, true));

setInterval(() => { if (!document.hidden && !working) sync(); }, 4000);
document.addEventListener('visibilitychange', () => {
  if (!client.connected) return;
  if (document.hidden) connection('Connected · polling paused', live ? 'connected' : 'stale');
  else sync();
});
window.addEventListener('pagehide', () => {
  session += 1; client.disconnect(); live = false; working = false; refreshing = null; loadingEvents = false;
  $('token').value = ''; $('connect-button').disabled = false; clearMessage(); connection('Disconnected'); renderDisconnected();
});
renderDisconnected();
