"""
ADK-compliant conversation callbacks for ImmoAssist.

Follows ADK best practices - minimal logic, leverages built-in session management.
ADK automatically handles session persistence and conversation history.
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
    ADK-compliant before-agent callback.

    ADK automatically manages session persistence and conversation history.
    We only handle application-specific state like language preferences.
    """
    try:
        state = callback_context.state

        # Initialize conversation state if needed
        if const.CONVERSATION_INITIALIZED not in state:
            _initialize_conversation_state(state)

        # Extract user input for processing
        user_input = _extract_user_input(callback_context)
        if not user_input:
            return None

        # Store current input (for application logic, not session management)
        state[const.CURRENT_USER_INPUT] = user_input

        # Application-specific state: language detection
        detected_language = detect_language(user_input)
        state[const.LANGUAGE_PREFERENCE] = detected_language

        # Application-specific state: translation requests
        is_translation, target_lang = is_translation_request(user_input)
        if is_translation:
            state[const.EXPLICIT_TRANSLATION_REQUEST] = True
            state[const.TRANSLATION_TARGET] = target_lang
        else:
            state[const.EXPLICIT_TRANSLATION_REQUEST] = False
            state[const.TRANSLATION_TARGET] = None

        # Application-specific state: course mode
        if is_course_mode_trigger(user_input):
            state[const.COURSE_MODE] = True
        elif is_course_mode_exit(user_input):
            state[const.COURSE_MODE] = False

        # Simple interaction counter (ADK handles full conversation history)
        state[const.INTERACTION_COUNT] = state.get(const.INTERACTION_COUNT, 0) + 1

        logger.debug(
            f"Processed input: lang={detected_language}, course={state.get(const.COURSE_MODE, False)}"
        )

        return None

    except Exception as e:
        logger.error(f"Error in before_agent_callback: {e}")
        return None


def after_agent_callback_simple(callback_context: CallbackContext) -> None:
    """
    ADK-compliant after-agent callback.

    ADK automatically handles session persistence and event recording.
    We only update application-specific state as needed.
    """
    try:
        state = callback_context.state

        if const.CONVERSATION_INITIALIZED not in state:
            return

        # Update last interaction timestamp for application logic
        state["last_interaction"] = datetime.now().isoformat()

        # Any application-specific cleanup can go here
        # ADK handles the actual conversation history and persistence

        logger.debug("Interaction processed successfully")

    except Exception as e:
        logger.error(f"Error in after_agent_callback: {e}")


def _initialize_conversation_state(state: Any) -> None:
    """Initialize application-specific conversation state.

    ADK handles session management, we only init our app-specific state.
    """
    state[const.CONVERSATION_INITIALIZED] = True
    state[const.SESSION_START_TIME] = datetime.now().isoformat()
    state[const.INTERACTION_COUNT] = 0
    state[const.COURSE_MODE] = False
    state[const.LANGUAGE_PREFERENCE] = "English"
    # Application-specific preferences
    state[const.USER_PREFERENCES] = {}
    logger.info("Application conversation state initialized")


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


# ADK automatically handles conversation history and agent responses
# No need for manual message history management
