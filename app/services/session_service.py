"""
Session management service for ImmoAssist.

Manages user sessions, conversation state, and persistent memory storage
using callback_context.state for ADK agent compatibility.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from google.adk.agents.callback_context import CallbackContext

from ..shared_libraries import conversation_constants as const

logger = logging.getLogger(__name__)


class SessionService:
    """
    Session management service providing persistent storage for user conversations
    and context management using ADK callback state patterns.
    """

    def __init__(self):
        """Initialize session service with default configuration."""
        self.default_session_timeout = timedelta(hours=24)
        self.max_conversation_history = 50
        logger.info("SessionService initialized")

    def initialize_session(self, callback_context: CallbackContext) -> Dict[str, Any]:
        """
        Initializes a new user session with default state structure.

        Args:
            callback_context: ADK callback context with state access

        Returns:
            Session initialization result with status and session details
        """
        try:
            state = callback_context.state

            # Check if session already exists
            if const.CONVERSATION_INITIALIZED in state:
                return {
                    "status": "existing",
                    "message": "Session already initialized",
                    "session_id": state.get("session_id", "unknown"),
                    "created_at": state.get(const.SESSION_START_TIME),
                }

            # Create new session
            session_id = str(uuid.uuid4())
            current_time = datetime.now().isoformat()

            # Initialize state structure
            state[const.CONVERSATION_INITIALIZED] = True
            state["session_id"] = session_id
            state[const.SESSION_START_TIME] = current_time
            state[const.GREETING_COUNT] = 0
            state[const.INTERACTION_COUNT] = 0
            state[const.CONVERSATION_PHASE] = const.PHASE_OPENING
            state[const.TOPICS_DISCUSSED] = []
            state[const.USER_PREFERENCES] = {}
            state[const.CONVERSATION_HISTORY] = []
            state[const.LAST_INTERACTION_TYPE] = const.INTERACTION_GREETING
            state["session_active"] = True
            state["last_activity"] = current_time

            # Initialize agent preference system
            state[const.PREFERRED_AGENT] = None
            state[const.AGENT_AUTO_MODE] = True

            # Initialize course mode
            state[const.COURSE_MODE] = False
            state[const.PRESENTATION_CONTEXT] = None

            logger.info(f"New session initialized: {session_id}")

            return {
                "status": "created",
                "message": "New session initialized successfully",
                "session_id": session_id,
                "created_at": current_time,
            }

        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return {
                "status": "error",
                "message": f"Session initialization failed: {str(e)}",
            }

    def get_session_info(self, callback_context: CallbackContext) -> Dict[str, Any]:
        """
        Retrieves current session information and statistics.

        Args:
            callback_context: ADK callback context with state access

        Returns:
            Session information with status and details
        """
        try:
            state = callback_context.state

            if const.CONVERSATION_INITIALIZED not in state:
                return {"status": "no_session", "message": "No active session found"}

            # Calculate session duration
            session_start = state.get(const.SESSION_START_TIME)
            current_time = datetime.now()

            session_duration = "unknown"
            if session_start:
                try:
                    start_dt = datetime.fromisoformat(session_start)
                    duration = current_time - start_dt
                    session_duration = str(duration).split(".")[
                        0
                    ]  # Remove microseconds
                except ValueError:
                    logger.warning(
                        f"Invalid session start time format: {session_start}"
                    )

            return {
                "status": "active",
                "session_id": state.get("session_id", "unknown"),
                "created_at": session_start,
                "session_duration": session_duration,
                "greeting_count": state.get(const.GREETING_COUNT, 0),
                "interaction_count": state.get(const.INTERACTION_COUNT, 0),
                "conversation_phase": state.get(
                    const.CONVERSATION_PHASE, const.PHASE_OPENING
                ),
                "topics_discussed": len(state.get(const.TOPICS_DISCUSSED, [])),
                "user_preferences": len(state.get(const.USER_PREFERENCES, {})),
                "conversation_history": len(state.get(const.CONVERSATION_HISTORY, [])),
                "last_interaction_type": state.get(
                    const.LAST_INTERACTION_TYPE, "unknown"
                ),
                "preferred_agent": state.get(const.PREFERRED_AGENT),
                "agent_auto_mode": state.get(const.AGENT_AUTO_MODE, True),
                "course_mode": state.get(const.COURSE_MODE, False),
                "session_active": state.get("session_active", True),
            }

        except Exception as e:
            logger.error(f"Error retrieving session info: {e}")
            return {
                "status": "error",
                "message": f"Session info retrieval failed: {str(e)}",
            }

    def update_session_activity(
        self, callback_context: CallbackContext
    ) -> Dict[str, Any]:
        """
        Updates session last activity timestamp and interaction counters.

        Args:
            callback_context: ADK callback context with state access

        Returns:
            Update operation result
        """
        try:
            state = callback_context.state

            if const.CONVERSATION_INITIALIZED not in state:
                return {
                    "status": "no_session",
                    "message": "No active session to update",
                }

            # Update activity timestamp
            current_time = datetime.now().isoformat()
            state["last_activity"] = current_time

            # Increment interaction count
            current_count = state.get(const.INTERACTION_COUNT, 0)
            state[const.INTERACTION_COUNT] = current_count + 1

            logger.debug(f"Session activity updated: interaction #{current_count + 1}")

            return {
                "status": "updated",
                "last_activity": current_time,
                "interaction_count": current_count + 1,
            }

        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
            return {"status": "error", "message": f"Session update failed: {str(e)}"}

    def get_conversation_history(
        self, callback_context: CallbackContext, limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieves conversation history from current session.

        Args:
            callback_context: ADK callback context with state access
            limit: Maximum number of interactions to return

        Returns:
            Conversation history with interactions and metadata
        """
        try:
            state = callback_context.state

            if const.CONVERSATION_INITIALIZED not in state:
                return {
                    "status": "no_session",
                    "message": "No active session for history retrieval",
                    "history": [],
                }

            history = state.get(const.CONVERSATION_HISTORY, [])

            # Apply limit if specified
            if limit and limit > 0:
                history = history[-limit:]  # Get last N interactions

            return {
                "status": "success",
                "session_id": state.get("session_id", "unknown"),
                "total_interactions": len(state.get(const.CONVERSATION_HISTORY, [])),
                "returned_interactions": len(history),
                "history": history,
            }

        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return {
                "status": "error",
                "message": f"History retrieval failed: {str(e)}",
                "history": [],
            }

    def set_preferred_agent(
        self, callback_context: CallbackContext, agent_key: str
    ) -> Dict[str, Any]:
        """
        Sets the preferred agent for the current session.

        Args:
            callback_context: ADK callback context with state access
            agent_key: Key identifying the preferred agent

        Returns:
            Operation result with status
        """
        try:
            state = callback_context.state

            if const.CONVERSATION_INITIALIZED not in state:
                return {
                    "status": "no_session",
                    "message": "No active session to update",
                }

            # Valid agent keys
            valid_agents = {
                "property_specialist",
                "calculator_specialist",
                "knowledge_specialist",
                "legal_specialist",
                "market_analyst",
                "presentation_specialist",
            }

            if agent_key and agent_key not in valid_agents:
                return {
                    "status": "invalid_agent",
                    "message": f"Invalid agent key: {agent_key}. Valid options: {', '.join(valid_agents)}",
                }

            # Set preferred agent
            state[const.PREFERRED_AGENT] = agent_key
            state[const.AGENT_AUTO_MODE] = agent_key is None

            logger.info(
                f"Preferred agent updated: {agent_key}, auto_mode: {agent_key is None}"
            )

            return {
                "status": "updated",
                "preferred_agent": agent_key,
                "agent_auto_mode": agent_key is None,
                "message": (
                    f"Preferred agent set to: {agent_key}"
                    if agent_key
                    else "Auto mode enabled"
                ),
            }

        except Exception as e:
            logger.error(f"Error setting preferred agent: {e}")
            return {
                "status": "error",
                "message": f"Failed to set preferred agent: {str(e)}",
            }

    def clear_session(self, callback_context: CallbackContext) -> Dict[str, Any]:
        """
        Clears the current session state (for testing or reset purposes).

        Args:
            callback_context: ADK callback context with state access

        Returns:
            Clear operation result
        """
        try:
            state = callback_context.state

            # Clear all session data
            keys_to_clear = [
                const.CONVERSATION_INITIALIZED,
                "session_id",
                const.SESSION_START_TIME,
                const.GREETING_COUNT,
                const.INTERACTION_COUNT,
                const.CONVERSATION_PHASE,
                const.TOPICS_DISCUSSED,
                const.USER_PREFERENCES,
                const.CONVERSATION_HISTORY,
                const.LAST_INTERACTION_TYPE,
                const.PREFERRED_AGENT,
                const.AGENT_AUTO_MODE,
                const.COURSE_MODE,
                const.PRESENTATION_CONTEXT,
                "session_active",
                "last_activity",
            ]

            for key in keys_to_clear:
                state.pop(key, None)

            logger.info("Session cleared successfully")

            return {
                "status": "cleared",
                "message": "Session state cleared successfully",
            }

        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            return {"status": "error", "message": f"Session clear failed: {str(e)}"}

    def save_conversation_interaction(
        self,
        callback_context: CallbackContext,
        user_input: str,
        agent_response: str,
        interaction_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Saves a conversation interaction to session history.

        Args:
            callback_context: ADK callback context with state access
            user_input: User's input message
            agent_response: Agent's response message
            interaction_type: Type of interaction (greeting, question, etc.)
            metadata: Additional interaction metadata

        Returns:
            Save operation result
        """
        try:
            state = callback_context.state

            if const.CONVERSATION_INITIALIZED not in state:
                return {
                    "status": "no_session",
                    "message": "No active session to save interaction",
                }

            # Create interaction record
            interaction_record = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "agent_response": agent_response,
                "interaction_type": interaction_type,
                "conversation_phase": state.get(const.CONVERSATION_PHASE, ""),
                "metadata": metadata or {},
            }

            # Add to conversation history
            if const.CONVERSATION_HISTORY not in state:
                state[const.CONVERSATION_HISTORY] = []

            state[const.CONVERSATION_HISTORY].append(interaction_record)

            # Maintain history size limit
            if len(state[const.CONVERSATION_HISTORY]) > self.max_conversation_history:
                # Remove oldest interactions
                excess_count = (
                    len(state[const.CONVERSATION_HISTORY])
                    - self.max_conversation_history
                )
                state[const.CONVERSATION_HISTORY] = state[const.CONVERSATION_HISTORY][
                    excess_count:
                ]
                logger.debug(f"Trimmed {excess_count} old interactions from history")

            logger.debug(f"Conversation interaction saved: {interaction_type}")

            return {
                "status": "saved",
                "interaction_id": len(state[const.CONVERSATION_HISTORY]) - 1,
                "timestamp": interaction_record["timestamp"],
            }

        except Exception as e:
            logger.error(f"Error saving conversation interaction: {e}")
            return {"status": "error", "message": f"Interaction save failed: {str(e)}"}

    def cleanup_expired_sessions(
        self, callback_context: CallbackContext
    ) -> Dict[str, Any]:
        """
        Cleans up expired session data based on activity timeout.

        Args:
            callback_context: ADK callback context with state access

        Returns:
            Cleanup operation result
        """
        try:
            state = callback_context.state

            if const.CONVERSATION_INITIALIZED not in state:
                return {"status": "no_session", "message": "No session to clean up"}

            # Check session expiration
            last_activity_str = state.get("last_activity")
            if not last_activity_str:
                return {
                    "status": "no_activity",
                    "message": "No activity timestamp found",
                }

            last_activity = datetime.fromisoformat(last_activity_str)
            current_time = datetime.now()
            time_since_activity = current_time - last_activity

            if time_since_activity > self.default_session_timeout:
                # Mark session as expired
                state["session_active"] = False
                state["expired_at"] = current_time.isoformat()

                logger.info(
                    f"Session expired: {state.get('session_id')} (inactive for {time_since_activity})"
                )

                return {
                    "status": "expired",
                    "message": "Session marked as expired due to inactivity",
                    "inactive_duration": str(time_since_activity),
                    "expired_at": state["expired_at"],
                }
            else:
                return {
                    "status": "active",
                    "message": "Session is still active",
                    "time_remaining": str(
                        self.default_session_timeout - time_since_activity
                    ),
                }

        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
            return {"status": "error", "message": f"Session cleanup failed: {str(e)}"}

    def export_session_data(self, callback_context: CallbackContext) -> Dict[str, Any]:
        """
        Exports complete session data for analysis or backup.

        Args:
            callback_context: ADK callback context with state access

        Returns:
            Complete session data export
        """
        try:
            state = callback_context.state

            if const.CONVERSATION_INITIALIZED not in state:
                return {"status": "no_session", "message": "No session data to export"}

            # Compile complete session data
            session_export = {
                "session_metadata": {
                    "session_id": state.get("session_id"),
                    "created_at": state.get(const.SESSION_START_TIME),
                    "last_activity": state.get("last_activity"),
                    "session_active": state.get("session_active", True),
                    "total_interactions": state.get(const.INTERACTION_COUNT, 0),
                    "session_duration": self._calculate_session_duration(
                        state.get(const.SESSION_START_TIME)
                    ),
                },
                "conversation_state": {
                    "current_phase": state.get(const.CONVERSATION_PHASE),
                    "greeting_count": state.get(const.GREETING_COUNT, 0),
                    "last_interaction_type": state.get(const.LAST_INTERACTION_TYPE),
                    "topics_discussed": state.get(const.TOPICS_DISCUSSED, []),
                },
                "user_preferences": state.get(const.USER_PREFERENCES, {}),
                "conversation_history": state.get(const.CONVERSATION_HISTORY, []),
                "export_timestamp": datetime.now().isoformat(),
            }

            return {
                "status": "success",
                "export_data": session_export,
                "data_size": len(json.dumps(session_export)),
            }

        except Exception as e:
            logger.error(f"Error exporting session data: {e}")
            return {
                "status": "error",
                "message": f"Session data export failed: {str(e)}",
            }

    def _calculate_session_duration(self, start_time_str: Optional[str]) -> str:
        """
        Calculates human-readable session duration.

        Args:
            start_time_str: ISO format start time string

        Returns:
            Human-readable duration string
        """
        try:
            if not start_time_str:
                return "unknown"

            start_time = datetime.fromisoformat(start_time_str)
            duration = datetime.now() - start_time

            total_minutes = int(duration.total_seconds() / 60)

            if total_minutes < 1:
                return "less than 1 minute"
            elif total_minutes < 60:
                return f"{total_minutes} minutes"
            else:
                hours = total_minutes // 60
                minutes = total_minutes % 60
                if minutes > 0:
                    return f"{hours}h {minutes}m"
                else:
                    return f"{hours}h"

        except Exception as e:
            logger.error(f"Error calculating session duration: {e}")
            return "calculation error"
