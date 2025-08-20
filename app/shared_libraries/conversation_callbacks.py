"""
Callback functions for conversation context management in ImmoAssist.

Uses callback_context.state for persistent memory storage following
ADK agent patterns for state management and conversation flow control.
"""

import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
import vertexai
from vertexai.preview.language_models import ChatModel

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.adk.tools import BaseTool

from app.config import config

from app.prompts import conversation_prompts
from . import conversation_constants as const

logger = logging.getLogger(__name__)


def combined_before_agent_callback(callback_context: CallbackContext) -> Optional[str]:
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


def before_agent_conversation_callback(
    callback_context: CallbackContext,
) -> Optional[str]:
    """
    Callback executed before each agent invocation.
    Analyzes conversation context and updates state for persistent memory.
    """
    try:
        state = callback_context.state

        # Extract user input from context
        user_input = _extract_user_input(callback_context)
        logger.info(f"BEFORE_AGENT_CALLBACK: Extracted user input: '{user_input}'")

        if not user_input:
            logger.warning(
                "BEFORE_AGENT_CALLBACK: No user input extracted, returning None"
            )
            return None

        # --- Сохранить пользовательский ввод в state для памяти ---
        state[const.CURRENT_USER_INPUT] = user_input
        logger.info(f"BEFORE_AGENT: Saved user input: '{user_input}'")

        # --- Обработка явных запросов на перевод ---
        explicit_translation_request = False
        translation_target = None
        user_input_lower = user_input.lower()
        # Примитивная проверка на явный запрос перевода (можно расширить)
        if (
            "переведи на русский" in user_input_lower
            or "перевести на русский" in user_input_lower
            or "translate to russian" in user_input_lower
            or "переведи на немецкий" in user_input_lower
            or "перевести на немецкий" in user_input_lower
            or "translate to german" in user_input_lower
            or "переведи на английский" in user_input_lower
            or "перевести на английский" in user_input_lower
            or "translate to english" in user_input_lower
        ):
            explicit_translation_request = True
            if "рус" in user_input_lower or "russian" in user_input_lower:
                translation_target = "Russian"
            elif "немец" in user_input_lower or "german" in user_input_lower:
                translation_target = "German"
            elif "англ" in user_input_lower or "english" in user_input_lower:
                translation_target = "English"
        state["explicit_translation_request"] = explicit_translation_request
        # Note: Language detection now happens in style_enhancer_callback
        if explicit_translation_request and translation_target:
            state["translation_target"] = translation_target
        else:
            state["translation_target"] = None

        # --- Установка/сброс режима курса (course_mode) ---
        course_mode_phrases = [
            "помоги с курсом",
            "объясни из курса",
            "разберём презентацию",
            "разберем презентацию",
            "по курсу",
            "по презентации",
            "курс",
            "презентация",
            "lesson",
            "course",
            "presentation",
        ]
        course_mode_off_phrases = [
            "теперь расскажи про рынок",
            "а что по налогам",
            "вне курса",
            "другая тема",
            "сменим тему",
            "расскажи про рынок",
            "расскажи про налоги",
            "расскажи про объекты",
            "про объекты",
            "про рынок",
            "про налоги",
            "market",
            "tax",
            "property",
            "object",
            "switch topic",
            "new topic",
        ]
        user_input_lower = user_input.lower()
        if any(phrase in user_input_lower for phrase in course_mode_phrases):
            state[const.COURSE_MODE] = True
        elif any(phrase in user_input_lower for phrase in course_mode_off_phrases):
            state[const.COURSE_MODE] = False

        # Store simple message history for recall (detailed analysis will happen in style_enhancer)
        message_history = state.get("message_history", [])
        message_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "message_number": len(message_history) + 1,
        }
        message_history.append(message_entry)
        state["message_history"] = message_history

        # Update basic counters
        state[const.INTERACTION_COUNT] = state.get(const.INTERACTION_COUNT, 0) + 1

        logger.debug(
            f"User input saved for memory. Translation request: {explicit_translation_request}"
        )

    except Exception as e:
        logger.error(f"Error in before_agent_conversation_callback: {e}")
    return None


def after_agent_conversation_callback(callback_context: CallbackContext) -> None:
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
        if hasattr(callback_context, "response") and callback_context.response:
            agent_response = getattr(callback_context.response, "text", None)
        if not agent_response and hasattr(callback_context, "agent_response"):
            agent_response = getattr(callback_context, "agent_response", None)
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
            "conversation_phase": state.get(const.CONVERSATION_PHASE, ""),
        }

        state[const.CONVERSATION_HISTORY].append(interaction_record)

        # Limit history to last 20 interactions
        if len(state[const.CONVERSATION_HISTORY]) > 20:
            state[const.CONVERSATION_HISTORY] = state[const.CONVERSATION_HISTORY][-20:]

        # Update message_history with agent response
        message_history = state.get("message_history", [])
        if message_history and agent_response:
            # Update the last entry with agent response
            if message_history[-1].get("agent_response") is None:
                message_history[-1]["agent_response"] = agent_response
            state["message_history"] = message_history

        logger.debug(f"Conversation interaction recorded: {interaction_type}")

    except Exception as e:
        logger.error(f"Error recording conversation interaction: {e}")


def conversation_style_enhancer_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """
    Callback for modifying LLM requests with conversation style considerations.
    Uses conversation state to provide contextual instructions.
    """
    try:
        state = callback_context.state
        logger.info(f"STYLE ENHANCER CALLED: State type: {type(state)}")

        # Initialize state if needed
        if const.CONVERSATION_INITIALIZED not in state:
            _initialize_conversation_state(state)

        # CRITICAL: Extract and analyze language from current LLM request
        current_user_input = None
        if llm_request and getattr(llm_request, "contents", None):
            for content in llm_request.contents:
                if getattr(content, "parts", None):
                    for part in content.parts:
                        if hasattr(part, "text") and part.text:
                            # Clean the text to get real user input
                            raw_text = part.text.strip()
                            current_user_input = _clean_user_input(raw_text)
                            logger.info(
                                f"STYLE ENHANCER: Extracted from LLM request: '{current_user_input}'"
                            )
                            break
                if current_user_input:
                    break

        # Detect language from current input if available
        detected_language = "English"  # default
        if current_user_input:
            detected_language = _analyze_language(current_user_input)
            state[const.LANGUAGE_PREFERENCE] = detected_language
            state[const.CURRENT_USER_INPUT] = current_user_input
            logger.info(
                f"STYLE ENHANCER LANGUAGE DETECTION: Input='{current_user_input}' -> Detected='{detected_language}'"
            )

        # Get current conversation context
        interaction_type = state.get(
            const.CURRENT_INTERACTION_TYPE, const.INTERACTION_ONGOING
        )
        conversation_phase = state.get(const.CONVERSATION_PHASE, const.PHASE_OPENING)
        greeting_count = state.get(const.GREETING_COUNT, 0)
        topics_discussed = state.get(const.TOPICS_DISCUSSED, [])
        user_preferences = state.get(const.USER_PREFERENCES, {})
        language_preference = state.get(const.LANGUAGE_PREFERENCE, detected_language)
        logger.info(f"STYLE ENHANCER: Final language: '{language_preference}'")
        explicit_translation_request = state.get("explicit_translation_request", False)
        translation_target = state.get("translation_target", None)

        # --- Языковая политика ---
        if explicit_translation_request and translation_target:
            enforced_language = translation_target
        else:
            enforced_language = language_preference

        # Generate contextual style instructions
        style_instructions = _build_style_instructions_from_state(
            interaction_type,
            conversation_phase,
            greeting_count,
            topics_discussed,
            user_preferences,
            enforced_language,
        )

        # --- Добавить строгие языковые инструкции ---
        language_block = (
            f"ABSOLUTE PRIORITY: The user wrote in {enforced_language} language. You MUST respond ONLY in {enforced_language}. "
            f"FORBIDDEN: Responding in any other language than {enforced_language}. "
            f"REQUIRED: Every single word in your response must be in {enforced_language}. "
            f"If you mention German real estate terms (like Grundbuch, Sonder-AfA) in non-German responses, add translation in parentheses."
        )

        # --- Добавить datetime напоминание если обнаружено ---
        datetime_reminder = state.get("datetime_reminder", "")
        if datetime_reminder:
            style_instructions = (
                f"{language_block}\n\n{datetime_reminder}\n\n{style_instructions}"
            )
            logger.info(
                "STYLE ENHANCER: Added datetime trigger reminder to instructions"
            )
        else:
            style_instructions = f"{language_block}\n\n{style_instructions}"

        # Add instructions to LLM request
        if style_instructions and getattr(llm_request, "contents", None):
            first_content = llm_request.contents[0]
            if getattr(first_content, "parts", None):
                original_text = getattr(first_content.parts[0], "text", "") or ""
                enhanced_text = f"{style_instructions}\n\n{original_text}"
                first_content.parts[0].text = enhanced_text

        logger.info(
            f"STYLE ENHANCER: Applied language={enforced_language}, instructions='{language_block[:100]}...'"
        )
        logger.debug(
            f"Style instructions applied: {interaction_type}, phase: {conversation_phase}, language: {enforced_language}, translation: {explicit_translation_request}"
        )

    except Exception as e:
        logger.error(f"Error in style enhancer callback: {e}")


def before_tool_conversation_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: CallbackContext
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
            "recall_conversation",
        ]

        if hasattr(tool, "name") and tool.name in tools_needing_context:
            # Add session context to tool arguments
            if "session_context" not in args:
                args["session_context"] = {
                    "conversation_phase": state.get(
                        const.CONVERSATION_PHASE, const.PHASE_OPENING
                    ),
                    "greeting_count": state.get(const.GREETING_COUNT, 0),
                    "topics_discussed": state.get(const.TOPICS_DISCUSSED, []),
                    "interaction_count": state.get(const.INTERACTION_COUNT, 0),
                }

        logger.debug(f"Tool context enhanced for: {getattr(tool, 'name', 'unknown')}")

    except Exception as e:
        logger.error(f"Error in tool context callback: {e}")

    return None


def _extract_user_input(callback_context: CallbackContext) -> Optional[str]:
    """Extracts user input from invocation context."""
    try:
        logger.info(f"EXTRACT_INPUT: Callback context type: {type(callback_context)}")
        logger.info(f"EXTRACT_INPUT: Available attributes: {dir(callback_context)}")

        # Method 0: Check for user_content attribute (ADK CallbackContext)
        if hasattr(callback_context, "user_content"):
            user_content = callback_context.user_content
            logger.info(
                f"EXTRACT_INPUT: user_content exists: {user_content is not None}"
            )
            logger.info(f"EXTRACT_INPUT: user_content type: {type(user_content)}")
            logger.info(f"EXTRACT_INPUT: user_content value: {repr(user_content)}")

            if user_content is not None:
                # user_content может быть строкой или содержать parts
                if isinstance(user_content, str):
                    text = user_content.strip()
                    logger.info(
                        f"EXTRACT_INPUT: user_content string: '{text[:100]}...'"
                    )
                    if text:  # Проверяем что строка не пустая
                        cleaned = _clean_user_input(text)
                        logger.info(
                            f"EXTRACT_INPUT: Returning cleaned from user_content: '{cleaned}'"
                        )
                        return cleaned
                elif hasattr(user_content, "parts") and user_content.parts:
                    logger.info(
                        f"EXTRACT_INPUT: user_content has {len(user_content.parts)} parts"
                    )
                    for i, part in enumerate(user_content.parts):
                        if hasattr(part, "text") and part.text:
                            text = part.text.strip()
                            logger.info(
                                f"EXTRACT_INPUT: user_content part {i} text: '{text[:100]}...'"
                            )
                            if text:  # Проверяем что текст не пустой
                                cleaned = _clean_user_input(text)
                                logger.info(
                                    f"EXTRACT_INPUT: Returning cleaned from user_content parts: '{cleaned}'"
                                )
                                return cleaned
                else:
                    # Проверим все атрибуты user_content
                    logger.info(
                        f"EXTRACT_INPUT: user_content attributes: {dir(user_content) if hasattr(user_content, '__dict__') else 'no attributes'}"
                    )

                    # Возможно это Content объект с parts или text напрямую
                    if hasattr(user_content, "text"):
                        text = str(user_content.text).strip()
                        logger.info(
                            f"EXTRACT_INPUT: user_content.text: '{text[:100]}...'"
                        )
                        if text:
                            cleaned = _clean_user_input(text)
                            logger.info(
                                f"EXTRACT_INPUT: Returning cleaned from user_content.text: '{cleaned}'"
                            )
                            return cleaned

        # Method 1: Check for request attribute (ADK CallbackContext)
        if hasattr(callback_context, "request"):
            request = callback_context.request
            logger.info(f"EXTRACT_INPUT: Found request attribute: {type(request)}")

            if hasattr(request, "messages") and request.messages:
                messages = request.messages
                logger.info(f"EXTRACT_INPUT: Found {len(messages)} messages in request")

                # Get the last user message
                for i, message in enumerate(reversed(messages)):
                    logger.info(
                        f"EXTRACT_INPUT: Message {i} role: {getattr(message, 'role', 'no role')}"
                    )
                    if hasattr(message, "role") and message.role == "user":
                        if hasattr(message, "parts") and message.parts:
                            logger.info(
                                f"EXTRACT_INPUT: Found {len(message.parts)} parts in user message"
                            )
                            for j, part in enumerate(message.parts):
                                if hasattr(part, "text") and part.text:
                                    text = part.text.strip()
                                    logger.info(
                                        f"EXTRACT_INPUT: Part {j} text: '{text[:100]}...'"
                                    )
                                    # Clean out language instructions that get prepended
                                    cleaned = _clean_user_input(text)
                                    logger.info(
                                        f"EXTRACT_INPUT: Returning cleaned: '{cleaned}'"
                                    )
                                    return cleaned

        # Method 2: Check _invocation_context (ADK internal)
        if (
            hasattr(callback_context, "_invocation_context")
            and callback_context._invocation_context
        ):
            invocation_context = callback_context._invocation_context
            logger.info(
                f"EXTRACT_INPUT: Found _invocation_context: {type(invocation_context)}"
            )

            if hasattr(invocation_context, "invocation_args"):
                invocation_args = invocation_context.invocation_args
                logger.info(
                    f"EXTRACT_INPUT: Found invocation_args in _invocation_context: {invocation_args is not None}"
                )

                if invocation_args and hasattr(invocation_args, "messages"):
                    messages = invocation_args.messages
                    logger.info(
                        f"EXTRACT_INPUT: Found {len(messages) if messages else 0} messages in _invocation_context"
                    )

                    if messages:
                        # Get the last user message
                        for i, message in enumerate(reversed(messages)):
                            logger.info(
                                f"EXTRACT_INPUT: _invocation_context Message {i} role: {getattr(message, 'role', 'no role')}"
                            )
                            if hasattr(message, "role") and message.role == "user":
                                if hasattr(message, "parts") and message.parts:
                                    logger.info(
                                        f"EXTRACT_INPUT: _invocation_context Found {len(message.parts)} parts in user message"
                                    )
                                    for j, part in enumerate(message.parts):
                                        if hasattr(part, "text") and part.text:
                                            text = part.text.strip()
                                            logger.info(
                                                f"EXTRACT_INPUT: _invocation_context Part {j} text: '{text[:100]}...'"
                                            )
                                            cleaned = _clean_user_input(text)
                                            logger.info(
                                                f"EXTRACT_INPUT: Returning cleaned from _invocation_context: '{cleaned}'"
                                            )
                                            return cleaned

        # Method 3: Check if there's a current message in invocation_args
        if hasattr(callback_context, "invocation_args"):
            invocation_args = callback_context.invocation_args
            logger.info(
                f"EXTRACT_INPUT: Found invocation_args: {invocation_args is not None}"
            )

            if invocation_args and hasattr(invocation_args, "messages"):
                messages = invocation_args.messages
                logger.info(
                    f"EXTRACT_INPUT: Found {len(messages) if messages else 0} messages"
                )

                if messages:
                    # Get the last user message
                    for i, message in enumerate(reversed(messages)):
                        logger.info(
                            f"EXTRACT_INPUT: Message {i} role: {getattr(message, 'role', 'no role')}"
                        )
                        if hasattr(message, "role") and message.role == "user":
                            if hasattr(message, "parts") and message.parts:
                                logger.info(
                                    f"EXTRACT_INPUT: Found {len(message.parts)} parts in user message"
                                )
                                for j, part in enumerate(message.parts):
                                    if hasattr(part, "text") and part.text:
                                        text = part.text.strip()
                                        logger.info(
                                            f"EXTRACT_INPUT: Part {j} text: '{text[:100]}...'"
                                        )
                                        # Clean out language instructions that get prepended
                                        cleaned = _clean_user_input(text)
                                        logger.info(
                                            f"EXTRACT_INPUT: Returning cleaned: '{cleaned}'"
                                        )
                                        return cleaned

        # Method 4: Check stored in state
        if (
            hasattr(callback_context, "state")
            and const.CURRENT_USER_INPUT in callback_context.state
        ):
            stored_input = callback_context.state[const.CURRENT_USER_INPUT]
            return _clean_user_input(stored_input)

        # Method 5: Extract from session events or context
        if hasattr(callback_context, "session") and callback_context.session:
            events = getattr(callback_context.session, "events", [])
            if events:
                # Get the most recent user event
                for event in reversed(events):
                    if hasattr(event, "content") and event.content:
                        parts = getattr(event.content, "parts", [])
                        if parts and hasattr(parts[0], "text"):
                            text = parts[0].text
                            return _clean_user_input(text)

        # Method 6: Fallback to context attributes
        if hasattr(callback_context, "user_input"):
            text = callback_context.user_input
            return _clean_user_input(text)

        logger.warning("Could not extract user input from any source")
        return None

    except Exception as e:
        logger.error(f"Error extracting user input: {e}")
        return None


def _clean_user_input(text: str) -> str:
    """Cleans user input by removing language enforcement instructions."""
    if not text:
        return text

    logger.info(f"CLEAN_INPUT: Original text: '{text}'")

    # If the text looks like a simple question without language instructions, return as-is
    if len(text) < 200 and not any(
        marker in text
        for marker in ["ABSOLUTE PRIORITY", "LANGUAGE ENFORCEMENT", "FORBIDDEN"]
    ):
        logger.info(f"CLEAN_INPUT: Simple text, returning as-is: '{text}'")
        return text

    # Remove language enforcement blocks that get prepended to user messages
    language_markers = [
        "ABSOLUTE PRIORITY:",
        "LANGUAGE ENFORCEMENT:",
        "FORBIDDEN: Responding in any other language",
        "REQUIRED: Every single word",
        "Zero tolerance for other languages",
        "Use warm, welcoming tone",
    ]

    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Check if this line contains language enforcement instructions
        is_language_instruction = any(marker in line for marker in language_markers)

        if not is_language_instruction:
            cleaned_lines.append(line)

    # Join the cleaned lines and return
    result = " ".join(cleaned_lines).strip()

    # If result is empty after cleaning, return original
    if not result:
        logger.warning(f"CLEAN_INPUT: Result empty, returning original: '{text}'")
        return text

    logger.info(f"CLEAN_INPUT: Cleaned result: '{result}'")
    return result


def _initialize_conversation_state(state: Any) -> None:
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
        state["message_history"] = []  # Добавляем инициализацию истории сообщений

        logger.info("Initialized conversation state")


def _analyze_interaction_type(user_input: str, state: Any) -> str:
    """Analyzes interaction type using an LLM."""
    try:
        # Initialize Vertex AI and the ChatModel
        vertexai.init()
        chat_model = ChatModel.from_pretrained(config.chat_model or "gemini-2.5-flash")

        prompt = conversation_prompts.ANALYZE_INTERACTION_TYPE_PROMPT.format(
            user_input=user_input
        )

        # Use the model to classify the interaction
        chat_session = chat_model.start_chat()
        response = chat_session.send_message(prompt)
        interaction_type = str(response.text).strip().lower()

        if "greeting" in interaction_type:
            greeting_count = state.get(const.GREETING_COUNT, 0)
            return (
                const.INTERACTION_REPEAT_GREETING
                if greeting_count > 0
                else const.INTERACTION_GREETING
            )
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
    """Analyzes the language of the user's input using simple heuristics and LLM fallback."""
    try:
        # First try simple heuristic detection for speed and reliability
        heuristic_result = _simple_language_heuristic(user_input)
        logger.info(
            f"HEURISTIC LANGUAGE DETECTION: Input='{user_input}' -> Detected='{heuristic_result}'"
        )

        # For German detection, use additional patterns
        user_input_lower = user_input.lower()
        german_patterns = [
            "ist",
            "was",
            "wie",
            "der",
            "die",
            "das",
            "und",
            "mit",
            "von",
            "zu",
            "auf",
            "für",
            "bei",
            "nach",
            "über",
        ]

        if any(pattern in user_input_lower for pattern in german_patterns):
            logger.info(f"GERMAN PATTERNS DETECTED in: '{user_input}'")
            return "German"

        # If heuristic is confident (Cyrillic/German chars), return it
        if heuristic_result in ["Russian", "German"]:
            return heuristic_result

        # For ambiguous cases, try LLM
        try:
            vertexai.init()
            chat_model = ChatModel.from_pretrained(
                config.chat_model or "gemini-2.5-flash"
            )

            prompt = conversation_prompts.ANALYZE_LANGUAGE_PROMPT.format(
                user_input=user_input
            )

            chat_session = chat_model.start_chat()
            response = chat_session.send_message(prompt)
            language_output = str(response.text).strip().capitalize()

            supported_languages = ["Russian", "German", "English"]
            if language_output in supported_languages:
                logger.info(
                    f"LLM LANGUAGE DETECTION: Input='{user_input}' -> Detected='{language_output}'"
                )
                return language_output
            else:
                logger.warning(f"LLM returned unsupported language: {language_output}")
                return "English"  # Default fallback

        except Exception as e:
            logger.error(f"Error in LLM language detection: {e}")
            return "English"  # Default fallback

    except Exception as e:
        logger.error(f"Error in language analysis: {e}")
        return "English"  # Safe fallback


def _simple_language_heuristic(text: str) -> str:
    """Enhanced language detection using character patterns and common words."""
    if not text:
        return "English"  # Default to English for empty text

    text_lower = text.lower()

    # Check for Cyrillic characters (Russian)
    cyrillic_chars = sum(1 for char in text if "\u0400" <= char <= "\u04ff")
    if cyrillic_chars > 0:
        return "Russian"

    # Check for German special characters
    german_chars = sum(1 for char in text if char in "äöüßÄÖÜ")
    if german_chars > 0:
        return "German"

    # Check for common German words that are distinctive
    german_words = [
        "ist",
        "was",
        "wie",
        "der",
        "die",
        "das",
        "und",
        "oder",
        "mit",
        "von",
        "für",
        "auf",
        "bei",
        "nach",
        "über",
        "können",
        "haben",
        "sein",
        "werden",
        "auch",
        "nicht",
        "nur",
        "noch",
        "alle",
        "diese",
        "einem",
        "einer",
        "eines",
        "unter",
        "zwischen",
        "während",
        "durch",
        "gegen",
        "ohne",
        "um",
        "aber",
        "doch",
        "schon",
    ]

    # Check for Russian words (transliterated or common)
    russian_words = [
        "что",
        "как",
        "где",
        "когда",
        "почему",
        "кто",
        "это",
        "для",
        "или",
        "так",
        "уже",
        "если",
        "все",
        "его",
        "ее",
        "их",
        "они",
        "мы",
        "вы",
        "не",
        "на",
        "в",
        "с",
        "по",
        "до",
        "из",
        "за",
        "под",
        "над",
        "при",
        "без",
        "через",
        "между",
    ]

    # Count word matches
    words = text_lower.split()
    german_word_count = sum(1 for word in words if word in german_words)
    russian_word_count = sum(1 for word in words if word in russian_words)

    # If we find German words, it's likely German
    if german_word_count > 0:
        return "German"

    # If we find Russian words, it's likely Russian
    if russian_word_count > 0:
        return "Russian"

    # Default to English for Latin alphabet without distinctive patterns
    return "English"


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


def _extract_topics_from_input(user_input: str) -> List[str]:
    """Extracts real estate topics from user input using domain patterns."""
    topics = []
    user_input_lower = user_input.lower()

    # Real estate domain patterns (multi-language)
    topic_patterns = {
        "investment": [
            "invest",
            "roi",
            "return",
            "profit",
            "yield",
            "инвестиции",
            "доходность",
            "investition",
            "rendite",
        ],
        "property_search": [
            "apartment",
            "house",
            "property",
            "квартира",
            "дом",
            "wohnung",
            "haus",
        ],
        "financing": [
            "mortgage",
            "loan",
            "credit",
            "financing",
            "ипотека",
            "кредит",
            "hypothek",
            "finanzierung",
        ],
        "location": [
            "location",
            "area",
            "district",
            "район",
            "местоположение",
            "lage",
            "bezirk",
        ],
    }

    for topic, keywords in topic_patterns.items():
        if any(keyword in user_input_lower for keyword in keywords):
            topics.append(topic)

    return topics


def _build_style_instructions_from_state(
    interaction_type: str,
    conversation_phase: str,
    greeting_count: int,
    topics_discussed: List[str],
    user_preferences: Dict[str, Any],
    language_preference: str,
) -> str:
    """Builds style instructions based on conversation state."""
    instructions = []

    # Force response language with absolute priority
    instructions.append(
        f"LANGUAGE ENFORCEMENT: Respond ONLY in {language_preference}. Zero tolerance for other languages."
    )

    # Phase-specific instructions
    if conversation_phase == const.PHASE_OPENING:
        instructions.append("Use warm, welcoming tone for initial conversation.")
    elif conversation_phase == const.PHASE_EXPLORATION:
        instructions.append(
            "Focus on understanding needs and providing informative responses."
        )
    elif conversation_phase == const.PHASE_DECISION:
        instructions.append(
            "Provide clear, actionable advice to support decision-making."
        )

    # Interaction-specific instructions
    if interaction_type == const.INTERACTION_REPEAT_GREETING:
        instructions.append("Keep greeting brief, transition to business quickly.")
    elif interaction_type == const.INTERACTION_QUESTION:
        instructions.append("Provide comprehensive, well-structured answers.")

    # Context-aware personalization
    if topics_discussed:
        topic_list = ", ".join(topics_discussed[:3])
        instructions.append(
            f"Reference previous discussion topics when relevant: {topic_list}"
        )

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
