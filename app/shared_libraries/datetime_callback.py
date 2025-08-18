"""
Datetime Callback for ImmoAssist - Automatic datetime tool triggering.

This callback automatically detects when a user message contains time-sensitive
content and ensures the agent uses the get_current_berlin_time tool.
"""

import re
from typing import Any, Dict, Optional
import logging
from google.adk.agents.invocation_context import InvocationContext

logger = logging.getLogger(__name__)

# Comprehensive datetime trigger patterns
DATETIME_TRIGGERS = [
    # Specific dates in various formats
    r"\b\d{1,2}\s+(декабря|января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября)\s+\d{4}\b",
    r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b",
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
    r"\b\d{4}\s*год[уаы]?\b",
    # Time references in Russian
    r"\b(сейчас|текущий момент|на данный момент|в настоящее время|на сегодня)\b",
    r"\b(актуальн|текущ|современн)[а-я]*\b",
    r"\b(недавно|в последнее время|в этом году|с начала года)\b",
    # Time references in English
    r"\b(currently|now|at present|nowadays|recently|this year|current)\b",
    r"\b(latest|up-to-date|actual|present-day)\b",
    # Legal and market timing
    r"\b(новый закон|изменения в законодательстве|актуальные ставки)\b",
    r"\b(new law|legal changes|current rates|market conditions)\b",
    r"\b(что изменилось|latest changes|recent updates)\b",
    # Questions about timing
    r"\b(когда|when|до какой даты|until when)\b.*\b(закон|law|regel|ставк|rate)\b",
]


def detect_datetime_triggers(message: str) -> bool:
    """
    Detect if a message contains datetime-sensitive content.

    Args:
        message: User's message text

    Returns:
        True if datetime tool should be triggered
    """
    message_lower = message.lower()

    for pattern in DATETIME_TRIGGERS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            logger.info(f"Datetime trigger detected: {pattern}")
            return True

    return False


def datetime_awareness_callback(callback_context: InvocationContext) -> Optional[str]:
    """
    Pre-agent callback that checks for datetime triggers and adds reminder.

    This callback examines the user's message and, if datetime-sensitive content
    is detected, stores a reminder in state to be used by style enhancer.
    """
    try:
        state = callback_context.state

        # Extract user input from context (using same method as existing callbacks)
        user_message = _extract_user_input_for_datetime(callback_context)

        if user_message and detect_datetime_triggers(user_message):
            # Store datetime reminder in state for style enhancer
            datetime_reminder = """
🚨 DATETIME TRIGGER DETECTED! 🚨

CRITICAL: The user's message contains time-sensitive content. You MUST:
1. IMMEDIATELY call get_current_berlin_time tool BEFORE answering
2. Compare any mentioned dates with the current date from the tool
3. Include current date context in your response
4. Never make assumptions about timing without verification

USER MESSAGE CONTAINS: Time-sensitive content requiring datetime verification.
"""

            state["datetime_reminder"] = datetime_reminder
            logger.info("Datetime trigger detected - reminder stored in state")

        return None

    except Exception as e:
        logger.error(f"Error in datetime_awareness_callback: {e}")
        return None


def _extract_user_input_for_datetime(
    callback_context: InvocationContext,
) -> Optional[str]:
    """Extract user input from invocation context for datetime detection."""
    try:
        # Use same extraction logic as existing callbacks
        if hasattr(callback_context, "invocation_args"):
            invocation_args = callback_context.invocation_args

            if invocation_args and hasattr(invocation_args, "messages"):
                messages = invocation_args.messages

                if messages:
                    # Get the last user message
                    for message in reversed(messages):
                        if hasattr(message, "role") and message.role == "user":
                            if hasattr(message, "parts") and message.parts:
                                for part in message.parts:
                                    if hasattr(part, "text") and part.text:
                                        return part.text.strip()

        # Fallback to state if available
        if hasattr(callback_context, "state"):
            return callback_context.state.get("CURRENT_USER_INPUT", None)

        return None

    except Exception as e:
        logger.error(f"Error extracting user input for datetime: {e}")
        return None
