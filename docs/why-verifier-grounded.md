# Let the model propose, but never decide

LLMs are good at *proposing*, new heuristics, candidate programs, mathematical
constructions. They're unreliable at *deciding* whether their own proposal is
correct. Most LLM pipelines collapse those two jobs into one: the model generates
an answer and you trust it. That's where hallucination lives.

FunSearch's insight was to split them. The model proposes; a **verifier** decides.
disco is an open, general implementation of that split.

## The loop

```
propose ──▶ verify ──▶ keep only what passed ──▶ evolve ──▶ propose ...
```

- **Propose.** A proposer suggests a candidate from the current best ones. It can
  be a mutation operator, a crossover, or an LLM. It is allowed to be wrong.
- **Verify.** A hard oracle returns `(valid, score)`. Unit tests, an exact
  combinatorial check, a simulator, a physical constraint, anything you trust.
- **Keep only what passed.** Invalid candidates are discarded. They never enter a
  population, so the search can't be corrupted by a bad (or hallucinated) proposal.
- **Evolve.** Island-model evolution concentrates the proposer's budget near
  candidates already proven to work, with migration for diversity.

The guarantee that falls out: **whatever disco returns is valid by construction,
and its score is real**, because it was measured by your verifier, not asserted
by a model.

## Why "keep only what passed" matters

If you let unverified candidates survive, one confident-but-wrong proposal
poisons every generation that descends from it. Gate hard on verification and the
worst a bad proposal can do is waste one evaluation. This is the same discipline
as property-based testing (generate wildly, assert invariants) or SAT/SMT-guided
synthesis (search freely, check hard), generation is cheap, verification is
ground truth.

It's also what makes an LLM proposer safe to use: it can be as creative as you
like, because it has no authority. Its output is a *hypothesis* until the verifier
certifies it.

## Does it actually find things?

Cap sets, subsets of `{0,1,2}^n` with no three points on a line, are a hard open
problem in combinatorics and FunSearch's headline example. disco's verifier is
exact, so every result is a provable cap. On AG(5,3), same evaluation budget:

| Method | Cap size (exactly verified) |
|---|---|
| Random restart | 39 |
| disco | 40 |

It reaches the proven maximum of 20 on AG(4,3). The edge over random restart
comes from a mutation operator that keeps a *heritable core* and only rebuilds the
periphery, a fully-greedy rebuild erases heritability and matches random. (This
is honest: with a mutation proposer disco is a good evolutionary searcher, not a
record-breaker. The point of the harness is that you plug in a smarter proposer,
an LLM, for problems where cleverness beats mutation.)

## Try it

```python
from disco import Discovery
from disco.problems import CapSet

problem = CapSet(4)
best = Discovery(problem, seed=0).run(80)
assert problem.is_cap(best.candidate)          # provably valid
print(best.score.value)                        # 20.0

# FunSearch mode: swap the proposer for a language model
from disco.proposers import LLMProposer
problem.propose = LLMProposer(complete=my_llm, render=my_prompt, parse=my_parser)
```

Code, tests, benchmark: https://github.com/ss1738/disco
