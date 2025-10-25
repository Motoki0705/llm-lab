"""FastAPI application that proxies chat requests to a local Ollama server."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .ollama_client import OllamaClient, OllamaClientError
from .schemas import (
    ChatHistoryResponse,
    ChatMessage,
    ChatRequest,
    SessionInitRequest,
    SessionResponse,
)
from .sessions import SessionManager, UnknownSessionError, session_manager


DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")


def get_session_manager() -> SessionManager:
    return session_manager


def get_ollama_client(request: Request) -> OllamaClient:
    return request.app.state.ollama_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(base_url=OLLAMA_URL, timeout=None) as http_client:
        app.state.ollama_client = OllamaClient(http_client, default_model=DEFAULT_MODEL)
        yield


def create_app() -> FastAPI:
    app = FastAPI(title="Local LLM Chat", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_headers=["*"],
        allow_methods=["*"],
        allow_credentials=True,
    )

    @app.get("/healthz")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/session", response_model=SessionResponse)
    async def create_session(
        payload: SessionInitRequest | None = None,
        manager: SessionManager = Depends(get_session_manager),
    ) -> SessionResponse:
        session_id = payload.session_id if payload else None
        resolved_session, created = await manager.ensure_session(session_id)
        return SessionResponse(session_id=resolved_session, created=created)

    @app.get("/api/session/{session_id}", response_model=ChatHistoryResponse)
    async def get_session_history(
        session_id: str,
        manager: SessionManager = Depends(get_session_manager),
    ) -> ChatHistoryResponse:
        try:
            history = await manager.get_history(session_id)
        except UnknownSessionError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown session")
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[ChatMessage(**message) for message in history],
        )

    @app.post("/api/chat")
    async def chat(
        request: ChatRequest,
        manager: SessionManager = Depends(get_session_manager),
        ollama: OllamaClient = Depends(get_ollama_client),
    ) -> StreamingResponse:
        session_id, _ = await manager.ensure_session(request.session_id)

        await manager.add_message(session_id, "user", request.message)
        conversation = await manager.get_history(session_id)

        async def response_stream() -> AsyncIterator[str]:
            assistant_chunks: list[str] = []
            try:
                async for chunk in ollama.stream_chat(
                    conversation,
                    model=request.model,
                    options=request.options,
                ):
                    assistant_chunks.append(chunk)
                    yield chunk
            except OllamaClientError as exc:
                # Surface a friendly message instead of aborting abruptly.
                yield f"\n[local-llm backend error] {exc}\n"
            else:
                if assistant_chunks:
                    await manager.add_message(session_id, "assistant", "".join(assistant_chunks))

        headers = {"X-Session-ID": session_id}
        return StreamingResponse(response_stream(), media_type="text/plain", headers=headers)

    return app


app = create_app()
