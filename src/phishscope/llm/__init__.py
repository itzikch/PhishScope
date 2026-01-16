"""
LLM module for PhishScope.

Provides multi-provider LLM client factory and prompts.
"""

from phishscope.llm.clients import get_chat_llm_client, is_llm_available
from phishscope.llm.clients.provider_type import LLMProviderType

__all__ = ["get_chat_llm_client", "is_llm_available", "LLMProviderType"]
