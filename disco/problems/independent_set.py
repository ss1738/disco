"""A small, exactly-solvable task -- max independent set on a path.

A 0/1 vector of length n with no two adjacent 1s, maximising the count of 1s.
The optimum is ``ceil(n/2)``, so tests can assert the engine reaches it. Handy as
a fast, deterministic sanity check for the search core.
"""

from __future__ import annotations

import random

from ..core import Score


class IndependentSet:
    """Max independent set on the path graph P_n.

    Args:
        n: Number of vertices.
    """

    def __init__(self, n: int) -> None:
        if n < 1:
            raise ValueError("n must be >= 1")
        self.n = n
        self.optimum = (n + 1) // 2

    def _valid(self, v) -> bool:
        return all(not (v[i] == 1 and v[i + 1] == 1) for i in range(len(v) - 1))

    def seed(self, rng: random.Random):
        return tuple(0 for _ in range(self.n))

    def propose(self, parents, rng: random.Random):
        v = list(parents[0]) if parents else [0] * self.n
        for _ in range(rng.randint(1, 3)):  # flip a few bits
            v[rng.randrange(self.n)] ^= 1
        for i in range(self.n - 1):  # repair adjacency
            if v[i] == 1 and v[i + 1] == 1:
                v[i + 1] = 0
        for i in range(self.n):  # greedy fill legal zeros
            left = i == 0 or v[i - 1] == 0
            right = i == self.n - 1 or v[i + 1] == 0
            if v[i] == 0 and left and right:
                v[i] = 1
        return tuple(v)

    def verify(self, candidate) -> Score:
        return Score(valid=self._valid(candidate), value=float(sum(candidate)))
