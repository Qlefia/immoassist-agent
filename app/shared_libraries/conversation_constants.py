"""
Conversation state constants for ImmoAssist.

These constants define the keys used in callback_context.state
for managing conversation context, user preferences, and interaction tracking.
"""

# Session management constants
CONVERSATION_INITIALIZED = "conversation_initialized"
SESSION_START_TIME = "session_start_time"
SESSION_ACTIVE = "session_active"
LAST_ACTIVITY = "last_activity"

# Conversation state tracking
GREETING_COUNT = "greeting_count"
INTERACTION_COUNT = "interaction_count"
CONVERSATION_PHASE = "conversation_phase"
CURRENT_USER_INPUT = "current_user_input"
LAST_INTERACTION_TYPE = "last_interaction_type"

# Agent preference system
PREFERRED_AGENT = "preferred_agent"
AGENT_AUTO_MODE = "agent_auto_mode"

# User preferences and memory
USER_PREFERENCES = "user_preferences"
TOPICS_DISCUSSED = "topics_discussed"
CONVERSATION_HISTORY = "conversation_history"

# Conversation phases
PHASE_OPENING = "opening"
PHASE_EXPLORATION = "exploration"
PHASE_DECISION = "decision"
PHASE_FOLLOW_UP = "follow_up"
PHASE_CLOSING = "closing"

# Interaction types
INTERACTION_GREETING = "greeting"
INTERACTION_QUESTION = "question"
INTERACTION_CALCULATION = "calculation"
INTERACTION_SEARCH = "search"
INTERACTION_LEGAL = "legal"
INTERACTION_ONGOING = "ongoing"
INTERACTION_REPEAT_GREETING = "repeat_greeting"
INTERACTION_CLOSING = "closing"

# Current interaction tracking
CURRENT_INTERACTION_TYPE = "current_interaction_type"

# Language and style tracking
LANGUAGE_PREFERENCE = "language_preference"
ENFORCED_LANGUAGE = "enforced_language"
EXPLICIT_TRANSLATION_REQUEST = "explicit_translation_request"
TRANSLATION_TARGET = "translation_target"
COMMUNICATION_STYLE = "communication_style"

# Course and presentation mode
COURSE_MODE = "course_mode"
PRESENTATION_CONTEXT = "presentation_context"
