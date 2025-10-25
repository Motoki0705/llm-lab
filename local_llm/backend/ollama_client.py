"""Thin asynchronous client for the local Ollama server."""

from __future__ import annotations

import json
from typing import AsyncIterator, Dict, List, Optional

import httpx


class OllamaClientError(RuntimeError):
    """Raised when the Ollama server responds with an error."""


class OllamaClient:
    """Wraps the Ollama HTTP API with an async streaming interface."""

    def __init__(self, http_client: httpx.AsyncClient, default_model: str) -> None:
        self._http_client = http_client
        self._default_model = default_model

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        *,
        model: Optional[str] = None,
        options: Optional[Dict[str, object]] = None,
    ) -> AsyncIterator[str]:
        """Stream chat completion chunks from Ollama.

        Parameters
        ----------
        messages:
            Conversation history in the format expected by Ollama's `/api/chat`.
        model:
            Optional override for the default model.
        options:
            Advanced generation parameters passed to Ollama.
        """

        payload: Dict[str, object] = {
            "model": model or self._default_model,
            "messages": messages,
            "stream": True,
        }
        if options:
            payload["options"] = options

        try:
            async with self._http_client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for raw_chunk in response.aiter_lines():
                    if not raw_chunk:
                        continue

                    # Ollama sometimes prefixes lines with "data: ".
                    if raw_chunk.startswith("data: "):
                        raw_chunk = raw_chunk[6:]

                    try:
                        data = json.loads(raw_chunk)
                    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                        # Skip malformed payloads but surface enough information for debugging.
                        raise OllamaClientError(f"Malformed chunk: {raw_chunk!r}") from exc

                    if data.get("error"):
                        raise OllamaClientError(str(data["error"]))

                    message = data.get("message") or {}
                    content = message.get("content")
                    if content:
                        yield content
        except httpx.HTTPStatusError as exc:
            raise OllamaClientError(
                f"Ollama returned status {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.HTTPError as exc:  # pragma: no cover - network errors
            raise OllamaClientError(str(exc)) from exc
