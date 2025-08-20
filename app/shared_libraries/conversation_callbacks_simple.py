"""
Simplified conversation callbacks for ImmoAssist.

Follows KISS principle - minimal logic in callbacks, delegates to services.
"""

import logging
from typing import Optional, Any
from datetime import datetime

from google.adk.agents.callback_context import CallbackContext
from . import conversation_constants as const
from .language_detector import (
    detect_language,
    is_translation_request,
    is_course_mode_trigger,
    is_course_mode_exit,
)

logger = logging.getLogger(__name__)


def before_agent_callback_simple(callback_context: CallbackContext) -> Optional[Any]:
    """
    Simplified before-agent callback.
    Initializes state and detects basic context without LLM calls.
    """
    try:
        state = callback_context.state

        # Initialize conversation state if needed
        if const.CONVERSATION_INITIALIZED not in state:
            _initialize_conversation_state(state)

        # Extract user input
        user_input = _extract_user_input(callback_context)
        if not user_input:
            return None

        # Store current input
        state[const.CURRENT_USER_INPUT] = user_input

        # Simple language detection
        detected_language = detect_language(user_input)
        state[const.LANGUAGE_PREFERENCE] = detected_language

        # Check for translation request
        is_translation, target_lang = is_translation_request(user_input)
        if is_translation:
            state[const.EXPLICIT_TRANSLATION_REQUEST] = True
            state[const.TRANSLATION_TARGET] = target_lang
        else:
            state[const.EXPLICIT_TRANSLATION_REQUEST] = False
            state[const.TRANSLATION_TARGET] = None

        # Check course mode triggers
        if is_course_mode_trigger(user_input):
            state[const.COURSE_MODE] = True
        elif is_course_mode_exit(user_input):
            state[const.COURSE_MODE] = False

        # Update interaction count
        state[const.INTERACTION_COUNT] = state.get(const.INTERACTION_COUNT, 0) + 1

        # Store in message history
        _add_to_message_history(state, user_input)

        logger.debug(
            f"Processed input: lang={detected_language}, course={state.get(const.COURSE_MODE, False)}"
        )

        return None

    except Exception as e:
        logger.error(f"Error in before_agent_callback: {e}")
        return None


def after_agent_callback_simple(callback_context: CallbackContext) -> None:
    """
    Simplified after-agent callback.
    Records interaction without complex processing.
    """
    try:
        state = callback_context.state

        if const.CONVERSATION_INITIALIZED not in state:
            return

        # Get stored user input
        user_input = state.get(const.CURRENT_USER_INPUT, "")
        if not user_input:
            return

        # Extract agent response (if available)
        agent_response = _extract_agent_response(callback_context)

        # Update message history with response
        if agent_response:
            message_history = state.get("message_history", [])
            if message_history and not message_history[-1].get("agent_response"):
                message_history[-1]["agent_response"] = agent_response
                state["message_history"] = message_history

        logger.debug("Interaction recorded")

    except Exception as e:
        logger.error(f"Error in after_agent_callback: {e}")


def _initialize_conversation_state(state: Any) -> None:
    """Initialize basic conversation state."""
    state[const.CONVERSATION_INITIALIZED] = True
    state[const.SESSION_START_TIME] = datetime.now().isoformat()
    state[const.GREETING_COUNT] = 0
    state[const.INTERACTION_COUNT] = 0
    state[const.CONVERSATION_PHASE] = const.PHASE_OPENING
    state[const.TOPICS_DISCUSSED] = []
    state[const.USER_PREFERENCES] = {}
    state[const.CONVERSATION_HISTORY] = []
    state["message_history"] = []
    state[const.COURSE_MODE] = False
    state[const.LANGUAGE_PREFERENCE] = "English"
    logger.info("Conversation state initialized")


def _extract_user_input(callback_context: CallbackContext) -> Optional[str]:
    """Extract user input from callback context."""
    try:
        # Check user_content attribute first
        if hasattr(callback_context, "user_content"):
            user_content = callback_context.user_content
            if user_content:
                if isinstance(user_content, str):
                    return user_content.strip()
                elif hasattr(user_content, "parts") and user_content.parts:
                    for part in user_content.parts:
                        if hasattr(part, "text") and part.text:
                            return str(part.text).strip()

        # Check state for stored input
        if hasattr(callback_context, "state"):
            stored = callback_context.state.get(const.CURRENT_USER_INPUT)
            if stored:
                return str(stored)

        return None

    except Exception as e:
        logger.error(f"Error extracting user input: {e}")
        return None


def _extract_agent_response(callback_context: CallbackContext) -> Optional[str]:
    """Extract agent response from callback context."""
    try:
        if hasattr(callback_context, "response") and callback_context.response:
            if hasattr(callback_context.response, "text"):
                return str(callback_context.response.text)

        if hasattr(callback_context, "agent_response"):
            return str(callback_context.agent_response)

        return None

    except Exception as e:
        logger.error(f"Error extracting agent response: {e}")
        return None


def _add_to_message_history(state: Any, user_input: str) -> None:
    """Add message to conversation history."""
    message_history = state.get("message_history", [])

    message_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "message_number": len(message_history) + 1,
    }

    message_history.append(message_entry)

    # Keep only last 50 messages
    if len(message_history) > 50:
        message_history = message_history[-50:]

    state["message_history"] = message_history
