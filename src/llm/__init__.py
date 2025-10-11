"""LLM layer для работы с языковыми моделями."""

from src.llm.client import LLMClient
from src.llm.protocols import LLMClientProtocol

__all__ = ["LLMClient", "LLMClientProtocol"]
