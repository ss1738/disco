"""disco vs random search on the cap set problem.

Both are given the same evaluation budget. Random search draws maximal caps from
random greedy orders (a strong baseline -- it already finds decent caps). disco
adds evolution + island migration on top of the same greedy operator. Every
number reported is an *exactly verified* cap size.

Run: python benchmarks/bench_capset.py
"""

from __future__ import annotations

import random

from disco import Discovery
from disco.problems import CapSet

N = 5  # AG(5,3): 243 points, best-known maximum cap = 45
SEED = 11


def random_search(problem: CapSet, budget: int, rng: random.Random) -> int:
    """Best exactly-verified cap from `budget` random greedy constructions."""
    best = 0
    for _ in range(budget):
        cand = problem.propose([], rng)  # greedy grow from empty
        score = problem.verify(cand)
        assert score.valid
        best = max(best, int(score.value))
    return best


def main() -> None:
    problem = CapSet(N)

    engine = Discovery(problem, islands=4, population=24, migrate_every=15, seed=SEED)
    best = engine.run(60)
    disco_size = int(best.score.value)
    budget = engine.evaluations  # give random search the same budget

    rng = random.Random(SEED)
    random_size = random_search(problem, budget, rng)

    print(f"problem:              cap set in AG({N},3)  ({3**N} points)")
    print("best-known maximum:   45")
    print(f"evaluation budget:    {budget}")
    print(f"random search:        {random_size}")
    print(f"disco (evolutionary): {disco_size}")
    print()
    print(f"returned cap is valid: {problem.is_cap(best.candidate)}  (re-verified)")
    print(f"size:                  {disco_size} points")


if __name__ == "__main__":
    main()
