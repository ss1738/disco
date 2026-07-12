"""Turn any LLM into a disco proposer -- this is what makes disco FunSearch.

You supply three small functions:

* ``complete(prompt) -> text`` -- any text model (OpenAI, Claude, a local model);
* ``render(parents) -> prompt`` -- how to show the current best candidates;
* ``parse(text) -> candidate`` -- how to read a candidate back out.

disco then asks the LLM to propose, and its verifier certifies the result.
A malformed or invalid completion simply fails verification and is dropped, so a
bad generation costs one evaluation and nothing else -- the search can never be
corrupted by a hallucinated candidate.
"""

from __future__ import annotations

import random
from typing import Any, Callable


class LLMProposer:
    """A ``propose`` callable backed by a language model.

    Args:
        complete: Maps a prompt string to a completion string (your LLM call).
        render: Maps the parent candidates to a prompt.
        parse: Maps a completion back to a candidate. May raise on malformed
            output; the exception is swallowed and the proposal is skipped.
    """

    def __init__(
        self,
        complete: Callable[[str], str],
        render: Callable[[list[Any]], str],
        parse: Callable[[str], Any],
    ) -> None:
        self.complete = complete
        self.render = render
        self.parse = parse

    def __call__(self, parents: list[Any], rng: random.Random) -> Any:
        try:
            return self.parse(self.complete(self.render(parents)))
        except Exception:
            # A bad generation is just a failed proposal; return an empty-ish
            # candidate that the verifier will reject, keeping the loop robust.
            return parents[0] if parents else None
