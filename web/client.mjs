/* The command protocol client. Authentication lives only in this module's memory. */
export class ProtocolError extends Error {
  constructor(code, message, status = 0, details = null, requestId = null) {
    super(message);
    this.name = 'ProtocolError';
    this.code = code;
    this.status = status;
    this.details = details;
    this.requestId = requestId;
  }
}

export class CommandClient {
  #token = '';
  #fetch;
  #state = null;
  #scope = null;
  #pending = null;
  #busy = false;
  #epoch = 0;
  #refreshNumber = 0;

  constructor(fetchImplementation = globalThis.fetch.bind(globalThis)) {
    this.#fetch = fetchImplementation;
  }

  get state() { return this.#state; }
  get scope() { return this.#scope; }
  get connected() { return Boolean(this.#token && this.#state); }
  get hasPending() { return this.#pending !== null; }
  get pendingId() { return this.#pending?.command_id || null; }
  get busy() { return this.#busy; }

  disconnect() {
    this.#epoch += 1;
    this.#token = '';
    this.#scope = null;
    this.#state = null;
    this.#pending = null;
    this.#busy = false;
  }

  async connect(token) {
    this.disconnect();
    if (typeof token !== 'string' || !token.trim()) {
      throw new ProtocolError('TOKEN_REQUIRED', 'Enter a bearer token to connect.');
    }
    this.#token = token.trim();
    const epoch = this.#epoch;
    try {
      return await this.refresh();
    } catch (error) {
      if (epoch === this.#epoch) this.disconnect();
      throw error;
    }
  }

  async #request(path, request = null) {
    if (!this.#token) throw new ProtocolError('DISCONNECTED', 'Connect before reading or changing the ledger.');
    if (!path.startsWith('/v1/') || path.startsWith('//')) {
      throw new ProtocolError('INVALID_ROUTE', 'Only local versioned API routes are supported.');
    }
    const epoch = this.#epoch;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), request ? 30000 : 15000);
    const options = {
      method: request ? 'POST' : 'GET',
      headers: { Authorization: 'Bearer ' + this.#token },
      credentials: 'omit', cache: 'no-store', mode: 'same-origin', redirect: 'error',
      signal: controller.signal,
    };
    if (request) {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(request);
    }
    try {
      const response = await this.#fetch(path, options);
      if (epoch !== this.#epoch) throw new ProtocolError('SESSION_CHANGED', 'The session changed while a request was in flight.');
      let body;
      try { body = await response.json(); } catch (_) {
        throw new ProtocolError('INVALID_RESPONSE', 'The service returned an unreadable response.', response.status);
      }
      if (epoch !== this.#epoch) throw new ProtocolError('SESSION_CHANGED', 'The session changed while a request was in flight.');
      if (!response.ok) {
        throw new ProtocolError(body?.error?.code || 'HTTP_ERROR', body?.error?.message || 'The request was refused.',
          response.status, body?.error?.details, body?.request_id);
      }
      const scope = response.headers.get('X-PolyIA-Scope');
      if (scope === 'operator' || scope === 'read') this.#scope = scope;
      return body;
    } catch (error) {
      if (error instanceof ProtocolError) throw error;
      if (epoch !== this.#epoch) throw new ProtocolError('SESSION_CHANGED', 'The session changed while a request was in flight.');
      throw new ProtocolError('CONNECTION_ERROR', request
        ? 'No command receipt was received. The command may have committed. Retry the same command ID to recover its receipt.'
        : 'The service could not be reached. Check the connection and refresh.');
    } finally {
      clearTimeout(timeout);
    }
  }

  read(path) { return this.#request(path); }

  async refresh() {
    const number = ++this.#refreshNumber;
    const state = await this.#request('/v1/state');
    if (!Number.isSafeInteger(state?.revision) || state.revision < 0 ||
        !/^[0-9a-f]{64}$/.test(state.head) || !state.requirements || !state.guidance) {
      throw new ProtocolError('INVALID_RESPONSE', 'The service response is not a versioned ledger state.');
    }
    if (number === this.#refreshNumber) this.#state = state;
    return this.#state;
  }

  async command(kind, payload) {
    if (!this.connected) throw new ProtocolError('DISCONNECTED', 'Connect and read the current revision first.');
    if (this.#scope !== 'operator') throw new ProtocolError('FORBIDDEN', 'This connection has read access only.');
    if (this.#pending) throw new ProtocolError('PENDING_COMMAND', 'Recover the pending command receipt before issuing another command.');
    if (!globalThis.crypto?.randomUUID) throw new ProtocolError('SECURE_CONTEXT_REQUIRED', 'Open the interface on loopback or HTTPS to create stable command IDs.');
    this.#pending = {
      command_id: 'web-' + globalThis.crypto.randomUUID(), expected_revision: this.#state.revision,
      kind, payload: structuredClone(payload),
    };
    return this.#sendPending();
  }

  async retry() {
    if (!this.#pending) throw new ProtocolError('NO_PENDING_COMMAND', 'There is no unresolved command to retry.');
    return this.#sendPending();
  }

  async #sendPending() {
    if (this.#busy) throw new ProtocolError('BUSY', 'A command request is already in progress.');
    this.#busy = true;
    const epoch = this.#epoch;
    try {
      const receipt = await this.#request('/v1/commands', this.#pending);
      if (receipt?.ok !== true || receipt.command_id !== this.#pending.command_id ||
          receipt.actor !== 'operator' || !Number.isSafeInteger(receipt.revision) ||
          receipt.revision !== this.#pending.expected_revision + 1 ||
          !/^[0-9a-f]{64}$/.test(receipt.head) || !receipt.result ||
          typeof receipt.result !== 'object' || Array.isArray(receipt.result)) {
        throw new ProtocolError('INVALID_RESPONSE', 'The service returned an incomplete or mismatched command receipt. Retry the same command ID to recover its recorded result.');
      }
      this.#pending = null;
      return receipt;
    } catch (error) {
      // The ledger looks up an exact committed ID before checking its revision.
      // A matching stale-revision refusal therefore conclusively rejects this
      // request. Pre-ledger/auth/proxy/parse errors cannot resolve an earlier
      // lost response, regardless of their HTTP status; keep the exact ID.
      if (epoch === this.#epoch && error.code === 'REVISION_CONFLICT' && error.status === 409 &&
          error.details?.expected_revision === this.#pending.expected_revision &&
          Number.isSafeInteger(error.details.current_revision) && error.details.current_revision >= 0 &&
          error.details.current_revision !== this.#pending.expected_revision) this.#pending = null;
      throw error;
    } finally {
      if (epoch === this.#epoch) this.#busy = false;
    }
  }
}
