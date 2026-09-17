"""Hermes plugin: strip foreign-script leaks, keep Russian/Latin/code."""

from __future__ import annotations

import sys
from pathlib import Path

_PLUGIN_DIR = Path(__file__).resolve().parent
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))

from sanitize import contains_foreign, sanitize as sanitize_response

# session_id -> skip sanitizing this turn (user already used a foreign script)
_skip_sessions: dict[str, bool] = {}


def reset_skip_flags() -> None:
    _skip_sessions.clear()


def on_pre_llm_call(
    user_message: str = "",
    session_id: str = "",
    **kwargs,
) -> None:
    """Remember whether this turn's prompt uses a script we would strip.

    Must return None: a string would be injected into the user message.
    """
    del kwargs
    _skip_sessions[session_id or ""] = contains_foreign(user_message or "")
    return None


def on_transform_llm_output(
    response_text: str = "",
    session_id: str = "",
    **kwargs,
) -> str | None:
    del kwargs
    if _skip_sessions.get(session_id or ""):
        return None
    return sanitize_response(response_text)


def register(ctx):
    ctx.register_hook("pre_llm_call", on_pre_llm_call)
    ctx.register_hook("transform_llm_output", on_transform_llm_output)
