"""Pydantic models shared by the backend routes."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User prompt text")
    session_id: Optional[str] = Field(
        default=None,
        description="Existing session identifier. When omitted a new session will be created.",
    )
    model: Optional[str] = Field(default=None, description="Override the default Ollama model")
    options: Optional[Dict[str, object]] = Field(
        default=None, description="Advanced generation parameters passed to Ollama"
    )


class SessionResponse(BaseModel):
    session_id: str
    created: bool


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]


class SessionInitRequest(BaseModel):
    session_id: Optional[str] = Field(default=None)
