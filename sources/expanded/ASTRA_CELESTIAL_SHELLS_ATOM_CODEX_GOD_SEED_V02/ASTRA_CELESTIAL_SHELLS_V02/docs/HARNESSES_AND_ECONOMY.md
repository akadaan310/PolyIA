# Harness architecture, social game theory, and economy

## Reusable adapter — no model lock-in

Expose machine control as an external **capability-checked** CLI or HTTP service with a small typed manifest. Model-driven systems (Codex, Hermes, OpenClaw, Claude Code, ChatGPT with tools) receive the `ATOM-HANDOFF/0.1` report, select ONE explicit next action, call the appropriate tool with typed arguments, and re-read the report. They do not get to declare checkpoints valid by textual assertion. In the demonstrator the live HTTP server is loopback only and unauthenticated; do NOT expose it to public networks.

Hermes' self-registering tools, toolsets, approval hooks, and persistent conversations are possible **external** adapters; OpenClaw's Gateway/tool policy/sandbox boundaries are another. Both are studies, **neither has been installed or linked** to this demo. ATOM's `atom.driver` is the independent *LLM-free harness-like execution loop* for a finite allowlisted plan. A genuine Hermes instance would need explicit installation, configuration, isolation, and operator approval. Never claim model-free means capable of autonomous language understanding.

Reference study:
- https://github.com/NousResearch/hermes-agent
- https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/tools-runtime.md
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/blob/main/docs/gateway/sandboxing.md

## Game theory and opportunities

A universal traversal is a *partially observable game state* when exploration data is incomplete. A player can explore, verify a scientific result, contribute a reusable artifact, or spend a bounded resource to run costly research. Policy choices must specify outcomes, uncertainty, costs, and a risk budget. Cooperative reward mechanisms, reputation, free-riding, adversarial submissions, proofs of contribution, and repeated games should be experimentally analyzed **before** any public economy. The pilot is only a declared maximin table; it is not a live marketplace.

## Token taxonomy

- **Control token**: typed automaton command with no monetary meaning.
- **Context token**: model tokenizer unit consumed during LLM inference; depends on model/provider.
- **Play credit**: currently implemented test-only, bounded, nonredeemable integer; no cash value, no on-chain value.
- **Computational unit**: future metered operation with a measured price in resources; not implemented.
- **Financial token or cryptoasset**: regulated/security-sensitive future business decision, not implemented.

A Bitcoin UTXO transaction spends previously created unspent outputs and creates new ones; Bitcoin does not make a normal game credit system safer or legally simpler by default. Start with a centralized auditable ledger, explicit refunds, abuse controls, consumer disclosures, and applicable payments/financial/legal review before any sale. The present app neither sells credits nor handles cryptocurrency.

Bitcoin source references (research only):
- https://github.com/bitcoin/bitcoin
- https://developer.bitcoin.org/devguide/transactions.html
