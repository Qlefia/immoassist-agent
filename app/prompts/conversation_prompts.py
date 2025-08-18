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
You are a language detection expert. Analyze the user's input and identify its primary language.

CRITICAL RULES:
1. You MUST respond with exactly ONE word: Russian, German, or English
2. Look at alphabet, grammar, and vocabulary patterns
3. For very short inputs (1-2 words), pay special attention to spelling patterns
4. Cyrillic alphabet = Russian
5. German specific patterns: ä, ö, ü, ß, compound words
6. English default for Latin alphabet without German patterns

Examples:
Short inputs:
- "Hi" → English
- "Hello" → English  
- "Hallo" → German
- "Привет" → Russian

Medium inputs:
- "What is the ROI?" → English
- "Wie hoch ist die Rendite?" → German
- "Что такое доходность?" → Russian

Be very confident in your decision. Even single words have language patterns.

User Input: "{user_input}"

Language:"""
