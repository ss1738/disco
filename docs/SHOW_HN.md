# Launch copy for disco

## Show HN title (pick one)
- **Show HN: disco – an open FunSearch (verifier-grounded discovery)**
- Show HN: disco – evolutionary search where only verifier-certified answers survive
- Show HN: Let an LLM propose, but never decide – open FunSearch harness

## Show HN body

DeepMind's FunSearch showed you can discover new results in maths and algorithms
by pairing an LLM (which proposes candidates) with an evaluator (which scores
them) and evolutionary search. The harness is closed. disco is a clean, general,
zero-dependency open version.

The one invariant it enforces: **only candidates a hard verifier certifies as
valid ever enter a population.** A proposer — mutation operator, crossover, or an
LLM — can be as creative or as wrong as it likes; anything that fails
verification is dropped and costs a single evaluation. So whatever disco returns
is *provably valid by construction*, and its reported score is real, not a model
claiming success.

You implement three methods (`seed`, `propose`, `verify`) and get island-model
evolution with tournament selection and migration for free. Swap the mutation
proposer for `LLMProposer(complete, render, parse)` and you have FunSearch.

The bundled example is cap sets — subsets of {0,1,2}^n with no 3 points on a line,
a hard open problem in combinatorics and FunSearch's headline result. The
verifier is exact. On AG(5,3) with the same evaluation budget: **random restart
39, disco 40** (every size independently re-verified); it reaches the proven
maximum 20 on AG(4,3).

Repo, tests, benchmark: <REPO_URL>

Honest notes: the win over random restart comes from a mutation operator that
preserves a *heritable core* — a naive fully-greedy rebuild matches random, and I
say so in the README (I hit exactly that while building it). disco is a search
*harness* with a validity guarantee; the intelligence lives in your proposer and
verifier. Feedback welcome, especially on the operator design and the LLM seam.

## First comment (post right after)

The design bet is that an LLM (or any proposer) should be allowed to be wrong,
because the verifier is the source of truth, not the model. That inverts the
usual "trust the model's output" flow: here the model's job is to generate
*hypotheses*, and nothing is believed until it's checked. It's the same instinct
behind property-based testing or SAT-guided synthesis — generation is cheap,
verification is ground truth, so gate hard on verification and let generation run
wild. The evolutionary layer is just there to concentrate the proposer's budget
near what's already verified to work.

## Where else to post
- r/MachineLearning ("[P] ..."), r/compsci
- X/Twitter: "FunSearch is closed. Here's an open, general version in ~250 lines"
  + the cap-set numbers
- lobste.rs (ml / compsci)
