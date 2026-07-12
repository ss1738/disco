"""Verifier-grounded evolutionary discovery.

A proposer suggests candidates; a **hard verifier** accepts or rejects each one;
island-based evolutionary search keeps improving. The core guarantee: **only
candidates the verifier certifies as valid ever survive.** Nothing hallucinated,
nothing unchecked, ever enters a population -- so whatever the engine returns is
provably valid by construction, and its reported score is real.

This is the open, general form of the FunSearch loop (LLM/proposer + evaluator +
evolution). The proposer is pluggable: a mutation operator, a crossover, or an
LLM. The verifier is yours -- unit tests, an exact combinatorial check, a
simulator, any oracle that returns a score.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class Score:
    """A verifier's verdict on one candidate.

    Args:
        valid: Whether the candidate passes the hard constraints. Invalid
            candidates are discarded and never enter a population.
        value: Objective to maximise (only meaningful when ``valid``).
    """

    valid: bool
    value: float


@dataclass
class Scored:
    """A candidate paired with its verified score."""

    candidate: Any
    score: Score


class Problem(Protocol):
    """What you implement to define a discovery task."""

    def seed(self, rng: random.Random) -> Any:
        """Return one valid starting candidate."""

    def propose(self, parents: list[Any], rng: random.Random) -> Any:
        """Return a new candidate derived from ``parents`` (1 or 2 of them)."""

    def verify(self, candidate: Any) -> Score:
        """The hard oracle: certify validity and score the candidate."""


class Discovery:
    """Island-model evolutionary search over verifier-certified candidates.

    Args:
        problem: The task (seed / propose / verify).
        islands: Independent populations (diversity; periodic migration).
        population: Candidates kept per island.
        tournament: Tournament size for parent selection.
        migrate_every: Copy each island's best into its neighbour this often
            (0 disables migration).
        seed: RNG seed for full reproducibility.
    """

    def __init__(
        self,
        problem: Problem,
        *,
        islands: int = 4,
        population: int = 24,
        tournament: int = 3,
        migrate_every: int = 15,
        seed: int = 0,
    ) -> None:
        if islands < 1 or population < 1:
            raise ValueError("islands and population must be >= 1")
        self.problem = problem
        self.islands = islands
        self.population = population
        self.tournament = tournament
        self.migrate_every = migrate_every
        self._rng = random.Random(seed)
        self._pops: list[list[Scored]] = []
        self.best: Scored | None = None
        self.evaluations = 0

    def _verify(self, candidate: Any) -> Scored | None:
        self.evaluations += 1
        try:
            score = self.problem.verify(candidate)
        except Exception:
            # A proposer (e.g. an LLM) that emits garbage must never crash the
            # search -- an unverifiable candidate is simply invalid.
            return None
        return Scored(candidate, score) if score.valid else None

    def _track(self, scored: Scored) -> bool:
        if self.best is None or scored.score.value > self.best.score.value:
            self.best = scored
            return True
        return False

    def _init(self) -> None:
        for _ in range(self.islands):
            pool: list[Scored] = []
            attempts = 0
            while len(pool) < self.population and attempts < self.population * 40:
                attempts += 1
                scored = self._verify(self.problem.seed(self._rng))
                if scored is not None:
                    pool.append(scored)
            if not pool:
                raise RuntimeError("seed() produced no valid candidate")
            pool.sort(key=lambda s: s.score.value, reverse=True)
            self._pops.append(pool)
            self._track(pool[0])

    def _tournament(self, pool: list[Scored]) -> Any:
        k = min(self.tournament, len(pool))
        contenders = self._rng.sample(pool, k)
        return max(contenders, key=lambda s: s.score.value).candidate

    def _migrate(self) -> None:
        bests = [pop[0] for pop in self._pops]
        for i in range(self.islands):
            incoming = bests[(i - 1) % self.islands]
            self._pops[i][-1] = incoming
            self._pops[i].sort(key=lambda s: s.score.value, reverse=True)

    def run(
        self,
        generations: int,
        *,
        target: float | None = None,
        on_improve: Callable[[int, Scored], None] | None = None,
    ) -> Scored:
        """Evolve for ``generations`` and return the best certified candidate.

        Args:
            generations: Number of generations.
            target: Stop early once the best value reaches this.
            on_improve: Called ``(generation, best)`` on every improvement.
        """
        if not self._pops:
            self._init()

        for gen in range(generations):
            for i in range(self.islands):
                pool = self._pops[i]
                children: list[Scored] = []
                tries = 0
                while len(children) < self.population and tries < self.population * 12:
                    tries += 1
                    n_parents = 1 if self._rng.random() < 0.5 else 2
                    parents = [self._tournament(pool) for _ in range(n_parents)]
                    scored = self._verify(self.problem.propose(parents, self._rng))
                    if scored is not None:
                        children.append(scored)

                merged = pool + children
                merged.sort(key=lambda s: s.score.value, reverse=True)
                self._pops[i] = merged[: self.population]

                if self._track(self._pops[i][0]) and on_improve is not None:
                    on_improve(gen, self.best)
                if target is not None and self.best is not None:
                    if self.best.score.value >= target:
                        return self.best

            if self.migrate_every and (gen + 1) % self.migrate_every == 0:
                self._migrate()

        assert self.best is not None
        return self.best
