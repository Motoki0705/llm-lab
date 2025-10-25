"""Entrypoint for running the FastAPI application with `python -m`."""

from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run(
        "local_llm.backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        factory=False,
    )


if __name__ == "__main__":
    main()

