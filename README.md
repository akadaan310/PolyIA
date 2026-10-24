# Poly IA: open the runtime branch

The extracted commission and deployed runtime are on **[codex/commission-20261024-83906c7](https://github.com/akadaan310/PolyIA/tree/codex/commission-20261024-83906c7)**. This default branch retains the original import transport; it is not the extracted runtime checkout.

Read the **[current safe-checkpoint handoff](https://github.com/akadaan310/PolyIA/blob/codex/commission-20261024-83906c7/docs/HANDOFF_2026-10-24.md)** for the actual live URL, deployed source, ledger checkpoint, access instructions, verification and unfinished work. Runtime 1.4.0 is live; the full mission remains **NOT_COMMISSIONED**. Commissioning stopped at the owner's request after verification. Continue only when the owner requests resumption.

For a new checkout:

```bash
git clone --branch codex/commission-20261024-83906c7 https://github.com/akadaan310/PolyIA.git
```

For an existing checkout, inspect and preserve local/concurrent work before switching. Do not re-import this transport over an existing runtime tree or initialize a replacement live ledger.

Then follow [START_HERE.md](https://github.com/akadaan310/PolyIA/blob/codex/commission-20261024-83906c7/START_HERE.md), [CODEX_START.md](https://github.com/akadaan310/PolyIA/blob/codex/commission-20261024-83906c7/CODEX_START.md), and the complete [GOD_SEED.md](https://github.com/akadaan310/PolyIA/blob/codex/commission-20261024-83906c7/GOD_SEED.md) on the runtime branch. All original sources are retained there. Infinity is IX; VII and VIII remain open research charters. The non-LLM core requirement and all unmet acceptance gates remain binding.

## Verified publication snapshot

- Final local handoff commit: `221d8aa9293d8107d2f0ff1fc17473819927f28d`.
- Published runtime commit: [`bb6319acb88467b618f5a6f673f1867768223ce6`](https://github.com/akadaan310/PolyIA/commit/bb6319acb88467b618f5a6f673f1867768223ce6).
- Exact shared content tree: `2e706ac118243efbea6ae0d55e1d854d980bc129`; 1,287 Git files, 1,286 release-manifest entries.
- Deployed runtime 1.4 source: `9667b6e9c9e9195fd8ac36fd2f22179e923ee0b8`.
- Live ledger revision **120**, checkpoint **cp-00000120**; accepted **2/192 mission requirements** (**4/194 total requirements**), **0 pending actionable guidance**.
- Research is **paused** at the owner's request. Full mission: **NOT_COMMISSIONED**.

The [sealed handoff](https://github.com/akadaan310/PolyIA/blob/bb6319acb88467b618f5a6f673f1867768223ce6/docs/HANDOFF_2026-10-24.md) records access instructions, verification evidence and unfinished work. This snapshot contains no credential values.
