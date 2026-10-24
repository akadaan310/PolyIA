"""Explicit cost accounting.

Every algorithm in ginsdk that reports a cost takes an optional ``Cost``
object and charges named, *counted* elementary steps to it.  The meaning of a
step is fixed by the function's docstring (for example "one limb operation on
w-bit words" or "one rewrite-rule application").  Wall-clock time is never
used as evidence of asymptotic cost (GIN-D-003).
"""
from __future__ import annotations

from collections import Counter


class Cost:
    """A bag of named counters.

    >>> c = Cost(); c.tick("add"); c.tick("add", 3); c["add"]
    4
    """

    def __init__(self) -> None:
        self.counts: Counter[str] = Counter()

    def tick(self, kind: str, k: int = 1) -> None:
        self.counts[kind] += k

    def __getitem__(self, kind: str) -> int:
        return self.counts[kind]

    def total(self, *kinds: str) -> int:
        if not kinds:
            return sum(self.counts.values())
        return sum(self.counts[k] for k in kinds)

    def as_dict(self) -> dict[str, int]:
        return dict(sorted(self.counts.items()))

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Cost({self.as_dict()})"


def charge(cost: Cost | None, kind: str, k: int = 1) -> None:
    """Charge ``k`` steps of ``kind`` if a cost object is present."""
    if cost is not None:
        cost.counts[kind] += k
