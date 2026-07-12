"""Tests for the discovery core and bundled problems."""

import random

import pytest

from disco import Discovery, Score, Scored
from disco.problems import CapSet, IndependentSet


def test_score_and_scored_types():
    s = Score(valid=True, value=3.0)
    assert s.valid and s.value == 3.0
    sc = Scored(candidate="x", score=s)
    assert sc.candidate == "x"


def test_bad_params_rejected():
    with pytest.raises(ValueError):
        Discovery(IndependentSet(4), islands=0)
    with pytest.raises(ValueError):
        Discovery(IndependentSet(4), population=0)


def test_independent_set_reaches_optimum():
    problem = IndependentSet(11)  # optimum = 6
    engine = Discovery(problem, islands=3, population=16, seed=1)
    best = engine.run(60)
    assert best.score.value == problem.optimum


def test_target_early_stop():
    problem = IndependentSet(9)  # optimum = 5
    engine = Discovery(problem, seed=2)
    best = engine.run(1000, target=5)
    assert best.score.value >= 5


def test_only_valid_candidates_survive():
    """Whatever disco returns must pass the verifier -- by construction."""
    problem = CapSet(3)
    engine = Discovery(problem, islands=2, population=10, seed=3)
    best = engine.run(30)
    assert best.score.valid is True
    assert problem.is_cap(best.candidate) is True  # independently re-checked


def test_reproducible_with_seed():
    a = Discovery(CapSet(3), seed=42).run(20).score.value
    b = Discovery(CapSet(3), seed=42).run(20).score.value
    assert a == b


def test_capset_verifier_is_exact():
    p = CapSet(2)  # AG(2,3): 9 points, max cap = 4
    # A known line (a, b, third(a,b)) must be rejected.
    a, b = (0, 0), (0, 1)
    line = frozenset({a, b, p._third(a, b)})
    assert p.is_cap(line) is False
    # Two points are always a cap.
    assert p.is_cap({a, b}) is True


def test_capset_finds_known_maximum_small():
    # AG(2,3) has maximum cap size 4; the engine should reach it.
    problem = CapSet(2)
    best = Discovery(problem, islands=3, population=12, seed=5).run(40)
    assert best.score.value == 4.0
    assert problem.is_cap(best.candidate)


def test_evaluations_are_counted():
    engine = Discovery(IndependentSet(6), seed=0)
    engine.run(10)
    assert engine.evaluations > 0
