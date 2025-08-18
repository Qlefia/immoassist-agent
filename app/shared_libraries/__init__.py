"""
Shared libraries для ImmoAssist.

Содержит общие компоненты и callback-функции для управления разговором.
"""

from .conversation_callbacks import (
    before_agent_conversation_callback,
    after_agent_conversation_callback,
    conversation_style_enhancer_callback,
    before_tool_conversation_callback,
)

__all__ = [
    "before_agent_conversation_callback",
    "after_agent_conversation_callback",
    "conversation_style_enhancer_callback",
    "before_tool_conversation_callback",
]
