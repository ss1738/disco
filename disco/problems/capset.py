"""The cap set problem -- FunSearch's headline example, with an exact verifier.

A *cap set* is a subset of the affine space AG(n, 3) = {0,1,2}^n containing no
three points on a line. Three distinct points a, b, c are collinear in this space
iff ``a + b + c ≡ 0 (mod 3)``, equivalently the third point of any pair (a, b) is
``-(a + b) mod 3``. Finding large cap sets is a hard open problem in combinatorics;
here the verifier is exact and cheap, so every returned set is a *provable* cap.
"""

from __future__ import annotations

import itertools
import random

from ..core import Score


class CapSet:
    """Discover a large cap set in AG(n, 3).

    Args:
        n: Dimension. The search space has ``3**n`` points.
    """

    def __init__(self, n: int) -> None:
        if n < 1:
            raise ValueError("n must be >= 1")
        self.n = n
        self.space: list[tuple[int, ...]] = [
            tuple(v) for v in itertools.product((0, 1, 2), repeat=n)
        ]

    def _third(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
        """The unique point collinear with distinct a, b."""
        return tuple((-a[i] - b[i]) % 3 for i in range(self.n))

    def is_cap(self, points) -> bool:
        """Exact check: no three points of ``points`` are collinear."""
        s = set(points)
        pts = list(s)
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if self._third(pts[i], pts[j]) in s:
                    return False
        return True

    def _addable(self, p: tuple[int, ...], s: set) -> bool:
        return all(self._third(p, a) not in s for a in s)

    def seed(self, rng: random.Random):
        return frozenset({rng.choice(self.space)})

    def propose(self, parents, rng: random.Random):
        # The operator keeps a heritable core and only rebuilds the periphery, so
        # good substructure propagates and evolution can beat random restart
        # (a fully-greedy rebuild would erase heritability -> no better than random).
        if len(parents) == 2:  # crossover: keep the larger parent's core, graft the other
            a, b = set(parents[0]), set(parents[1])
            larger, other = (a, b) if len(a) >= len(b) else (b, a)
            base = {p for p in larger if rng.random() > 0.2}  # partial teardown
            for p in other:
                if p not in base and self._addable(p, base):
                    base.add(p)
        elif parents:  # mutation: drop ~15% of the periphery, then regrow
            base = set(parents[0])
            drop = max(1, int(len(base) * 0.15))
            for p in rng.sample(list(base), min(drop, len(base))):
                base.discard(p)
        else:  # fresh construction (used for seeding / random-restart baseline)
            base = set()

        order = self.space[:]  # greedy grow to a maximal cap along a random order
        rng.shuffle(order)
        for p in order:
            if p not in base and self._addable(p, base):
                base.add(p)
        return frozenset(base)

    def verify(self, candidate) -> Score:
        return Score(valid=self.is_cap(candidate), value=float(len(candidate)))
