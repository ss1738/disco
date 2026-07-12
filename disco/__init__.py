"""disco -- verifier-grounded evolutionary discovery.

An open, general form of the FunSearch loop: a pluggable proposer suggests
candidates, a hard verifier certifies them, and island-model evolution keeps
improving. Only verifier-certified candidates ever survive, so whatever disco
returns is provably valid by construction.
"""

from .core import Discovery, Problem, Score, Scored

__version__ = "0.1.0"
__all__ = ["Discovery", "Problem", "Score", "Scored", "__version__"]
