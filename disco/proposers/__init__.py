"""Pluggable proposers. Mutation operators live on each Problem; the LLM
adapter here turns disco into FunSearch."""

from .llm import LLMProposer

__all__ = ["LLMProposer"]
