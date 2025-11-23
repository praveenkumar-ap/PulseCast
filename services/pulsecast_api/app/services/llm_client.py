from __future__ import annotations

import logging
import time
from typing import Optional

from ..core.config import settings

logger = logging.getLogger(__name__)


class LLMNotConfiguredError(Exception):
    """Raised when LLM provider is not configured or disabled."""


class LLMClientError(Exception):
    """Generic LLM client failure."""


def _build_headers(api_key: Optional[str]) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def generate_completion(
    prompt: str,
    *,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> str:
    """
    Generate a completion using the configured LLM provider.

    Raises:
        LLMNotConfiguredError: if provider is "none" or missing config.
        LLMClientError: on provider call failure.
    """
    provider = settings.llm_provider.lower() if settings.llm_provider else "none"
    model = settings.llm_model_name
    if provider == "none" or not model:
        raise LLMNotConfiguredError("LLM provider not configured")

    # Only OpenAI-compatible path implemented for now.
    if provider in {"openai", "azure_openai"}:
        try:
            import openai  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise LLMNotConfiguredError("openai package not installed") from exc

        client = openai.Client(api_key=settings.llm_api_key, base_url=settings.llm_endpoint or None)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or settings.llm_max_tokens,
            "temperature": temperature if temperature is not None else settings.llm_temperature,
        }
        start = time.time()
        try:
            resp = client.chat.completions.create(**payload)
            latency = time.time() - start
            logger.info(
                "LLM call success provider=%s model=%s latency_ms=%.1f",
                provider,
                model,
                latency * 1000,
            )
            content = resp.choices[0].message.content if resp and resp.choices else ""
            if not content:
                raise LLMClientError("Empty completion from LLM")
            return content
        except Exception as exc:  # noqa: BLE001
            logger.error("LLM call failed provider=%s model=%s", provider, model, exc_info=exc)
            raise LLMClientError(str(exc)) from exc

    raise LLMNotConfiguredError(f"Unsupported LLM provider: {provider}")
