"""LLM client module for different providers."""

import os
import logging
from typing import Dict, Optional, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from phishscope.llm.clients.provider_type import LLMProviderType
from phishscope.config import settings


logger = logging.getLogger(__name__)


def _get_provider() -> LLMProviderType:
    """Get the configured LLM provider."""
    provider_str = settings.LLM_PROVIDER.lower()
    try:
        return LLMProviderType(provider_str)
    except ValueError:
        logger.warning(f"Unknown LLM provider: {provider_str}, defaulting to watsonx")
        return LLMProviderType.WATSONX


def is_llm_available() -> bool:
    """Check if LLM is available and properly configured."""
    return settings.is_llm_configured()


def _get_base_llm_settings(model_name: str, model_parameters: Optional[Dict]) -> Dict:
    """Get base LLM settings for the configured provider."""
    if model_parameters is None:
        model_parameters = {}

    provider = _get_provider()

    if provider == LLMProviderType.OLLAMA:
        parameters = {
            "num_predict": model_parameters.get("max_tokens", 1024),
            "temperature": model_parameters.get("temperature", 0.05),
        }
        return {
            "model": model_name,
            "base_url": settings.OLLAMA_BASE_URL,
            **parameters,
        }

    if provider == LLMProviderType.WATSONX:
        parameters = {
            "max_new_tokens": model_parameters.get("max_tokens", 800),
            "decoding_method": model_parameters.get("decoding_method", "greedy"),
            "temperature": model_parameters.get("temperature", 0.5),
            "repetition_penalty": model_parameters.get("repetition_penalty", 1.0),
            "top_k": model_parameters.get("top_k", 50),
            "top_p": model_parameters.get("top_p", 0.9),
            "stop_sequences": model_parameters.get("stop_sequences", []),
        }
        return {
            "url": settings.WATSONX_API_ENDPOINT,
            "project_id": settings.WATSONX_PROJECT_ID,
            "apikey": settings.WATSONX_API_KEY,
            "model_id": model_name,
            "params": parameters,
        }

    if provider == LLMProviderType.RITS:
        parameters = {
            "max_tokens": model_parameters.get("max_tokens", 800),
            "temperature": model_parameters.get("temperature", 0.5),
            "top_p": model_parameters.get("top_p", 0.9),
        }
        return {
            "base_url": f"{settings.RITS_API_BASE_URL}/v1",
            "model": model_name,
            "api_key": settings.RITS_API_KEY,
            "extra_body": parameters,
        }

    if provider == LLMProviderType.OPENAI:
        return {
            "model": model_name,
            "api_key": settings.OPENAI_API_KEY,
            "max_tokens": model_parameters.get("max_tokens", 800),
            "temperature": model_parameters.get("temperature", 0.5),
        }

    raise ValueError(f"Unsupported LLM provider: {provider}")


def get_chat_llm_client(
    model_name: Optional[str] = None,
    model_parameters: Optional[Dict] = None,
) -> Any:
    """
    Get a chat LLM client based on the configured provider.

    Uses lazy imports to avoid loading unnecessary dependencies.

    Args:
        model_name: The name of the model to use. If not provided,
                   uses default for the provider.
        model_parameters: Optional model parameters.

    Returns:
        The LLM client instance.
    """
    provider = _get_provider()

    # Set default model names per provider
    if model_name is None:
        default_models = {
            LLMProviderType.WATSONX: settings.WATSONX_MODEL_ID,
            LLMProviderType.RITS: "rits/openai/gpt-oss-120b",
            LLMProviderType.OPENAI: "gpt-4o-mini",
            LLMProviderType.OLLAMA: "llama3.2",
        }
        model_name = settings.LLM_MODEL or default_models.get(provider, "llama3.2")

    logger.info(f"Initializing LLM client: provider={provider.value}, model={model_name}")

    if provider == LLMProviderType.OLLAMA:
        from langchain_ollama import ChatOllama  # pylint: disable=import-outside-toplevel

        return ChatOllama(
            **_get_base_llm_settings(model_name=model_name, model_parameters=model_parameters)
        )

    if provider == LLMProviderType.RITS:
        from langchain_openai import ChatOpenAI  # pylint: disable=import-outside-toplevel

        return ChatOpenAI(
            **_get_base_llm_settings(model_name=model_name, model_parameters=model_parameters)
        )

    if provider == LLMProviderType.WATSONX:
        from langchain_ibm import ChatWatsonx  # pylint: disable=import-outside-toplevel

        return ChatWatsonx(
            **_get_base_llm_settings(model_name=model_name, model_parameters=model_parameters)
        )

    if provider == LLMProviderType.OPENAI:
        from langchain_openai import ChatOpenAI  # pylint: disable=import-outside-toplevel

        return ChatOpenAI(
            **_get_base_llm_settings(model_name=model_name, model_parameters=model_parameters)
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")
