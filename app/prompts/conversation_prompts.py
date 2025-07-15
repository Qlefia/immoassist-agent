"""
Prompts for conversation analysis and interaction classification.

This module contains structured prompts used to guide the LLM in understanding
and classifying user interactions within the conversation.
"""

# Prompt for analyzing the type of interaction from the user's input.
# This prompt instructs the LLM to classify the input into one of several
# predefined categories, allowing for more nuanced conversational flow management
# than simple keyword matching.
ANALYZE_INTERACTION_TYPE_PROMPT = """
Analyze the user's input to determine the interaction type. Classify it into ONE of the following categories:
- "greeting": For standard greetings (hello, good morning, etc.).
- "question": If the input is a question or seeks information.
- "closing": For farewells or closing statements (bye, thank you, etc.).
- "ongoing": For any other statement or continuation of the conversation.

User Input: "{user_input}"

Category:
"""

# Prompt for detecting the language of the user's input.
# This helps ensure the agent's response language matches the user's language.
ANALYZE_LANGUAGE_PROMPT = """
Analyze the user's input and identify its primary language. CRITICAL: Choose ONLY from this list: [Russian, German, English]. Respond with the single best language name from the list.

User Input: "{user_input}"

Language:
""" 