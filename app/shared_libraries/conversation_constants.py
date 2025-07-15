"""
Conversation state management constants for ImmoAssist.

Defines keys for storing conversation data in callback_context.state
following ADK agent patterns for state management.
"""

# Core conversation state keys
CONVERSATION_INITIALIZED = "conversation_initialized"
CONVERSATION_HISTORY = "conversation_history"
GREETING_COUNT = "greeting_count"
TOPICS_DISCUSSED = "topics_discussed"
USER_PREFERENCES = "user_preferences"
CONVERSATION_PHASE = "conversation_phase"
LAST_INTERACTION_TYPE = "last_interaction_type"
SESSION_START_TIME = "session_start_time"

# Current interaction context
CURRENT_USER_INPUT = "current_user_input"
CURRENT_ANALYSIS = "current_analysis"
CURRENT_INTERACTION_TYPE = "current_interaction_type"

# Conversation analytics
INTERACTION_COUNT = "interaction_count"
LANGUAGE_PREFERENCE = "language_preference"
COMMUNICATION_STYLE = "communication_style"

# Conversation phases
PHASE_OPENING = "opening"
PHASE_EXPLORATION = "exploration" 
PHASE_DECISION = "decision"
PHASE_CLOSING = "closing"

# Interaction types
INTERACTION_GREETING = "greeting"
INTERACTION_REPEAT_GREETING = "repeat_greeting"
INTERACTION_ONGOING = "ongoing"
INTERACTION_QUESTION = "question"
INTERACTION_REPEAT_QUESTION = "repeat_question"
INTERACTION_CLOSING = "closing"

# Communication tone levels
TONE_FORMAL = "formal"
TONE_SEMI_FORMAL = "semi_formal"
TONE_CASUAL = "casual"
TONE_FRIENDLY = "friendly" 