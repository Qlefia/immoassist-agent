"""
Callback functions for conversation context management in ImmoAssist.

Uses callback_context.state for persistent memory storage following
ADK agent patterns for state management and conversation flow control.
"""

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime
import vertexai
from vertexai.preview.language_models import ChatModel

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models import LlmRequest
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext

from app.config import config

from app.prompts import conversation_prompts
from . import conversation_constants as const

logger = logging.getLogger(__name__)


def combined_before_agent_callback(callback_context: InvocationContext) -> Optional[str]:
    """
    Composite callback combining memory initialization and conversation analysis.
    Called before each agent invocation to ensure proper context setup.
    """
    try:
        state = callback_context.state
        
        # Initialize memory if needed
        if const.CONVERSATION_INITIALIZED not in state:
            _initialize_conversation_state(state)
        
        # Analyze current input and update context
        return before_agent_conversation_callback(callback_context)
        
    except Exception as e:
        logger.error(f"Error in combined before agent callback: {e}")
        return None


def before_agent_conversation_callback(callback_context: InvocationContext) -> Optional[str]:
    """
    Callback executed before each agent invocation.
    Analyzes conversation context and updates state for persistent memory.
    """
    try:
        state = callback_context.state
        
        # Extract user input from context
        user_input = _extract_user_input(callback_context)
        if not user_input:
            return None
        
        # --- Язык всегда определяется по последнему сообщению пользователя ---
        language = _analyze_language(user_input)
        state[const.LANGUAGE_PREFERENCE] = language
        state["last_detected_language"] = language

        # --- Обработка явных запросов на перевод ---
        explicit_translation_request = False
        translation_target = None
        user_input_lower = user_input.lower()
        # Примитивная проверка на явный запрос перевода (можно расширить)
        if (
            "переведи на русский" in user_input_lower or
            "перевести на русский" in user_input_lower or
            "translate to russian" in user_input_lower or
            "переведи на немецкий" in user_input_lower or
            "перевести на немецкий" in user_input_lower or
            "translate to german" in user_input_lower or
            "переведи на английский" in user_input_lower or
            "перевести на английский" in user_input_lower or
            "translate to english" in user_input_lower
        ):
            explicit_translation_request = True
            if "рус" in user_input_lower or "russian" in user_input_lower:
                translation_target = "Russian"
            elif "немец" in user_input_lower or "german" in user_input_lower:
                translation_target = "German"
            elif "англ" in user_input_lower or "english" in user_input_lower:
                translation_target = "English"
        state["explicit_translation_request"] = explicit_translation_request
        if explicit_translation_request and translation_target:
            state[const.LANGUAGE_PREFERENCE] = translation_target
            state["translation_target"] = translation_target
        else:
            state["translation_target"] = None

        # --- Остальной существующий код ---
        # Analyze interaction type and conversation phase
        interaction_type = _analyze_interaction_type(user_input, state)
        conversation_phase = _determine_conversation_phase(interaction_type, state)
        
        # Update counters and context
        state[const.INTERACTION_COUNT] = state.get(const.INTERACTION_COUNT, 0) + 1
        state[const.CURRENT_USER_INPUT] = user_input
        state[const.CURRENT_INTERACTION_TYPE] = interaction_type
        state[const.CONVERSATION_PHASE] = conversation_phase
        
        # Handle greetings
        if interaction_type in [const.INTERACTION_GREETING, const.INTERACTION_REPEAT_GREETING]:
            state[const.GREETING_COUNT] = state.get(const.GREETING_COUNT, 0) + 1
        
        # Extract and store discussed topics
        topics = _extract_topics_from_input(user_input)
        existing_topics = state.get(const.TOPICS_DISCUSSED, [])
        for topic in topics:
            if topic not in existing_topics:
                existing_topics.append(topic)
        state[const.TOPICS_DISCUSSED] = existing_topics
        
        # Store last interaction type
        state[const.LAST_INTERACTION_TYPE] = interaction_type
        
        logger.debug(f"Conversation context updated: {interaction_type}, phase: {conversation_phase}, language: {language}, translation: {explicit_translation_request}")
        
    except Exception as e:
        logger.error(f"Error in before_agent_conversation_callback: {e}")
    return None


def after_agent_conversation_callback(
    callback_context: InvocationContext
) -> None:
    """
    Callback executed after agent response generation.
    Updates conversation history and context in state storage.
    """
    try:
        state = callback_context.state
        
        if const.CONVERSATION_INITIALIZED not in state:
            return
            
        # Get current context
        user_input = state.get(const.CURRENT_USER_INPUT, "")
        interaction_type = state.get(const.CURRENT_INTERACTION_TYPE, "")
        
        if not user_input:
            return
        
        # Extract agent response from callback context
        agent_response = None
        if hasattr(callback_context, 'response') and callback_context.response:
            agent_response = getattr(callback_context.response, 'text', None)
        if not agent_response and hasattr(callback_context, 'agent_response'):
            agent_response = getattr(callback_context, 'agent_response', None)
        if not agent_response:
            agent_response = ""
        
        # Update conversation history
        if const.CONVERSATION_HISTORY not in state:
            state[const.CONVERSATION_HISTORY] = []
            
        # Add interaction to history
        interaction_record = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "agent_response": agent_response,
            "interaction_type": interaction_type,
            "conversation_phase": state.get(const.CONVERSATION_PHASE, "")
        }
        
        state[const.CONVERSATION_HISTORY].append(interaction_record)
        
        # Limit history to last 20 interactions
        if len(state[const.CONVERSATION_HISTORY]) > 20:
            state[const.CONVERSATION_HISTORY] = state[const.CONVERSATION_HISTORY][-20:]
        
        logger.debug(f"Conversation interaction recorded: {interaction_type}")
        
    except Exception as e:
        logger.error(f"Error recording conversation interaction: {e}")


def conversation_style_enhancer_callback(
    callback_context: CallbackContext, 
    llm_request: LlmRequest
) -> None:
    """
    Callback for modifying LLM requests with conversation style considerations.
    Uses conversation state to provide contextual instructions.
    """
    try:
        state = callback_context.state
        
        # Check if state is initialized
        if const.CONVERSATION_INITIALIZED not in state:
            return
        
        # Get current conversation context
        interaction_type = state.get(const.CURRENT_INTERACTION_TYPE, const.INTERACTION_ONGOING)
        conversation_phase = state.get(const.CONVERSATION_PHASE, const.PHASE_OPENING)
        greeting_count = state.get(const.GREETING_COUNT, 0)
        topics_discussed = state.get(const.TOPICS_DISCUSSED, [])
        user_preferences = state.get(const.USER_PREFERENCES, {})
        language_preference = state.get(const.LANGUAGE_PREFERENCE, "German") # Default to German
        explicit_translation_request = state.get("explicit_translation_request", False)
        translation_target = state.get("translation_target", None)

        # --- Языковая политика ---
        if explicit_translation_request and translation_target:
            enforced_language = translation_target
        else:
            enforced_language = language_preference

        # Generate contextual style instructions
        style_instructions = _build_style_instructions_from_state(
            interaction_type, conversation_phase, greeting_count, 
            topics_discussed, user_preferences, enforced_language
        )

        # --- Добавить строгие языковые инструкции ---
        language_block = (
            f"CRITICAL: ALWAYS reply in the language of the user's last message ('{enforced_language}'), unless the user explicitly requests a translation. "
            f"If you use German terms in a Russian or English answer, ALWAYS provide a brief translation in parentheses right after the term. "
            f"NEVER mix languages in one sentence, except for German terms with translation."
        )
        style_instructions = f"{language_block}\n\n{style_instructions}"

        # Add instructions to LLM request
        if style_instructions and llm_request.contents:
            first_content = llm_request.contents[0]
            if first_content.parts:
                original_text = first_content.parts[0].text or ""
                enhanced_text = f"{style_instructions}\n\n{original_text}"
                first_content.parts[0].text = enhanced_text
        
        logger.debug(f"Style instructions applied: {interaction_type}, phase: {conversation_phase}, language: {enforced_language}, translation: {explicit_translation_request}")
        
    except Exception as e:
        logger.error(f"Error in style enhancer callback: {e}")


def before_tool_conversation_callback(
    tool: BaseTool, 
    args: Dict[str, Any], 
    tool_context: CallbackContext
) -> Optional[str]:
    """
    Callback executed before tool invocation.
    Adds conversation context to tools that support it.
    """
    try:
        state = tool_context.state
        
        if const.CONVERSATION_INITIALIZED not in state:
            return None
            
        # Add conversation context for specific tools
        tools_needing_context = [
            "analyze_conversation_context",
            "memorize_conversation", 
            "recall_conversation"
        ]
        
        if hasattr(tool, 'name') and tool.name in tools_needing_context:
            # Add session context to tool arguments
            if 'session_context' not in args:
                args['session_context'] = {
                    'conversation_phase': state.get(const.CONVERSATION_PHASE, const.PHASE_OPENING),
                    'greeting_count': state.get(const.GREETING_COUNT, 0),
                    'topics_discussed': state.get(const.TOPICS_DISCUSSED, []),
                    'interaction_count': state.get(const.INTERACTION_COUNT, 0)
                }
                
        logger.debug(f"Tool context enhanced for: {getattr(tool, 'name', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Error in tool context callback: {e}")
        
    return None


def _extract_user_input(callback_context: InvocationContext) -> Optional[str]:
    """Extracts user input from invocation context."""
    try:
        # Extract from session events or context
        if hasattr(callback_context, 'session') and callback_context.session:
            events = getattr(callback_context.session, 'events', [])
            if events:
                # Get the most recent user event
                for event in reversed(events):
                    if hasattr(event, 'content') and event.content:
                        parts = getattr(event.content, 'parts', [])
                        if parts and hasattr(parts[0], 'text'):
                            return parts[0].text
                            
        # Fallback: try to get from context attributes
        if hasattr(callback_context, 'user_input'):
            return callback_context.user_input
            
        return None
        
    except Exception as e:
        logger.error(f"Error extracting user input: {e}")
        return None


def _initialize_conversation_state(state: Dict[str, Any]) -> None:
    """Initializes conversation state following ADK patterns."""
    if const.CONVERSATION_INITIALIZED not in state:
        state[const.CONVERSATION_INITIALIZED] = True
        state[const.SESSION_START_TIME] = datetime.now().isoformat()
        state[const.GREETING_COUNT] = 0
        state[const.INTERACTION_COUNT] = 0
        state[const.CONVERSATION_PHASE] = const.PHASE_OPENING
        state[const.TOPICS_DISCUSSED] = []
        state[const.USER_PREFERENCES] = {}
        state[const.LAST_INTERACTION_TYPE] = const.INTERACTION_GREETING
        
        logger.info("Initialized conversation state")


def _analyze_interaction_type(user_input: str, state: Dict[str, Any]) -> str:
    """Analyzes interaction type using an LLM."""
    try:
        # Initialize Vertex AI and the ChatModel
        vertexai.init()
        chat_model = ChatModel.from_pretrained(config.chat_model)

        prompt = conversation_prompts.ANALYZE_INTERACTION_TYPE_PROMPT.format(
            user_input=user_input
        )
        
        # Use the model to classify the interaction
        response = chat_model.chat(prompt)
        interaction_type = response.text.strip().lower()

        if "greeting" in interaction_type:
            greeting_count = state.get(const.GREETING_COUNT, 0)
            return const.INTERACTION_REPEAT_GREETING if greeting_count > 0 else const.INTERACTION_GREETING
        elif "question" in interaction_type:
            return const.INTERACTION_QUESTION
        elif "closing" in interaction_type:
            return const.INTERACTION_CLOSING
        else:
            return const.INTERACTION_ONGOING

    except Exception as e:
        logger.error(f"Error analyzing interaction type with LLM: {e}")
        # Fallback to a simple default if LLM fails
        return const.INTERACTION_ONGOING


def _analyze_language(user_input: str) -> str:
    """Analyzes the language of the user's input using an LLM."""
    try:
        # Initialize Vertex AI and the ChatModel
        vertexai.init()
        chat_model = ChatModel.from_pretrained(config.chat_model)

        prompt = conversation_prompts.ANALYZE_LANGUAGE_PROMPT.format(
            user_input=user_input
        )
        
        # Use the model to classify the language
        response = chat_model.chat(prompt)
        language_output = response.text.strip().capitalize()
        
        # Directly return the detected language.
        # Add a whitelist to prevent unexpected values.
        supported_languages = ["Russian", "German", "English"]
        if language_output in supported_languages:
            return language_output
        else:
            # Fallback to German if detection is unclear or unsupported.
            logger.warning(f"Unsupported language detected: '{language_output}'. Defaulting to German.")
            return "German"

    except Exception as e:
        logger.error(f"Error analyzing language with LLM: {e}")
        # Fallback to German if LLM fails.
        return "German"


def _determine_conversation_phase(interaction_type: str, state: Dict[str, Any]) -> str:
    """Determines conversation phase based on interaction type and state."""
    if interaction_type == const.INTERACTION_GREETING:
        return const.PHASE_OPENING
    elif interaction_type == const.INTERACTION_CLOSING:
        return const.PHASE_CLOSING
    
    # Use state context to determine phase
    interaction_count = state.get(const.INTERACTION_COUNT, 0)
    topics_discussed = state.get(const.TOPICS_DISCUSSED, [])
    
    if interaction_count <= 2:
        return const.PHASE_OPENING
    elif len(topics_discussed) > 2 and interaction_count > 5:
        return const.PHASE_DECISION
    else:
        return const.PHASE_EXPLORATION


def _extract_topics_from_input(user_input: str) -> list:
    """Extracts real estate topics from user input using domain patterns."""
    topics = []
    user_input_lower = user_input.lower()
    
    # Real estate domain patterns (multi-language)
    topic_patterns = {
        "investment": ["invest", "roi", "return", "profit", "yield", "инвестиции", "доходность", "investition", "rendite"],
        "property_search": ["apartment", "house", "property", "квартира", "дом", "wohnung", "haus"],
        "financing": ["mortgage", "loan", "credit", "financing", "ипотека", "кредит", "hypothek", "finanzierung"],
        "location": ["location", "area", "district", "район", "местоположение", "lage", "bezirk"]
    }
    
    for topic, keywords in topic_patterns.items():
        if any(keyword in user_input_lower for keyword in keywords):
            topics.append(topic)
    
    return topics


def _build_style_instructions_from_state(
    interaction_type: str, 
    conversation_phase: str, 
    greeting_count: int,
    topics_discussed: list,
    user_preferences: dict,
    language_preference: str
) -> str:
    """Builds style instructions based on conversation state."""
    instructions = []
    
    # Force response language
    instructions.append(f"CRITICAL: The user's language is {language_preference}. Your entire response MUST be in {language_preference}.")
    
    # Phase-specific instructions
    if conversation_phase == const.PHASE_OPENING:
        instructions.append("Use warm, welcoming tone for initial conversation.")
    elif conversation_phase == const.PHASE_EXPLORATION:
        instructions.append("Focus on understanding needs and providing informative responses.")
    elif conversation_phase == const.PHASE_DECISION:
        instructions.append("Provide clear, actionable advice to support decision-making.")
    
    # Interaction-specific instructions
    if interaction_type == const.INTERACTION_REPEAT_GREETING:
        instructions.append("Keep greeting brief, transition to business quickly.")
    elif interaction_type == const.INTERACTION_QUESTION:
        instructions.append("Provide comprehensive, well-structured answers.")
    
    # Context-aware personalization
    if topics_discussed:
        topic_list = ", ".join(topics_discussed[:3])
        instructions.append(f"Reference previous discussion topics when relevant: {topic_list}")
    
    if user_preferences:
        instructions.append("Consider established user preferences in your response.")
    
    return " ".join(instructions) if instructions else ""


def _calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculates simple text similarity for context awareness."""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0 