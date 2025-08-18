"""
Enhanced callback system for ImmoAssist with combined functionality.

Combines datetime integration, conversation management, and memory callbacks
into unified system for better agent coordination.
"""

import json
import logging
from typing import Optional

from google.adk.agents.callback_context import CallbackContext

from .conversation_callbacks import (
    before_agent_conversation_callback,
    after_agent_conversation_callback as original_after_agent_callback,
)
from .datetime_callback import datetime_awareness_callback
from . import conversation_constants as const

logger = logging.getLogger(__name__)


def enhanced_before_agent_callback(callback_context: CallbackContext) -> Optional[str]:
    """
    Enhanced before-agent callback combining all functionality.

    Provides comprehensive pre-processing including:
    - Datetime validation and context injection
    - Conversation management and memory
    - Agent preference extraction and storage

    Args:
        callback_context: The callback context from the agent invocation

    Returns:
        Optional response content if early termination is needed

    Raises:
        Exception: Logs but does not raise exceptions to prevent agent disruption
    """
    try:
        # Extract and store preferred agent from request if present
        _extract_and_store_preferred_agent(callback_context)

        # Apply datetime validation
        datetime_result = datetime_awareness_callback(callback_context)
        if datetime_result:
            logger.info("Datetime context added to conversation")

        # Apply conversation callback
        conversation_result = before_agent_conversation_callback(callback_context)
        if conversation_result:
            logger.info("Conversation context processed")

        return None

    except Exception as e:
        logger.error(f"Error in enhanced before agent callback: {e}")
        return None


def _extract_and_store_preferred_agent(callback_context: CallbackContext) -> None:
    """
    Extracts preferredAgent from request and stores it in session state.

    Args:
        callback_context: ADK callback context with access to request and state
    """
    try:
        state = callback_context.state

        # Try to extract preferred agent from different possible locations
        preferred_agent = None

        # Check if callback_context has request information
        if hasattr(callback_context, "request"):
            request = callback_context.request
            if hasattr(request, "body") and request.body:
                try:
                    # Try to parse request body
                    if isinstance(request.body, str):
                        body_data = json.loads(request.body)
                    else:
                        body_data = request.body

                    preferred_agent = body_data.get("preferredAgent")
                except (json.JSONDecodeError, AttributeError):
                    pass

        # Check alternative locations for preferred agent
        if not preferred_agent and hasattr(callback_context, "parameters"):
            preferred_agent = callback_context.parameters.get("preferredAgent")

        # Check if it's in the state already (from previous interactions)
        if not preferred_agent:
            preferred_agent = state.get(const.PREFERRED_AGENT)

        # Store in state if found
        if preferred_agent:
            state[const.PREFERRED_AGENT] = preferred_agent
            state[const.AGENT_AUTO_MODE] = False
            logger.info(f"Preferred agent set: {preferred_agent}")
        else:
            # Set auto mode if no preferred agent
            if const.AGENT_AUTO_MODE not in state:
                state[const.AGENT_AUTO_MODE] = True

        logger.debug(
            f"Agent preference state: auto_mode={state.get(const.AGENT_AUTO_MODE, True)}, preferred={state.get(const.PREFERRED_AGENT, 'none')}"
        )

    except Exception as e:
        logger.error(f"Error extracting preferred agent: {e}")


def after_agent_conversation_callback(callback_context) -> None:
    """
    Enhanced after-agent callback for cleanup and state management.
    """
    try:
        # Run existing after-agent callback
        original_after_agent_callback(callback_context)

        # Additional cleanup or state management can go here
        logger.debug("Enhanced after-agent callback completed")
    except Exception as e:
        logger.error(f"Error in enhanced after agent callback: {e}")
