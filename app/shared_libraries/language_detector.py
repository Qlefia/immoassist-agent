"""
Simple language detection module for ImmoAssist.

Provides lightweight language detection without LLM calls in callbacks.
Follows KISS principle - simple heuristics-based detection.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect language using simple heuristics.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Detected language: "Russian", "German", or "English"
    """
    if not text:
        return "English"
    
    text_lower = text.lower()
    
    # Check for Cyrillic characters (Russian)
    if any('\u0400' <= char <= '\u04FF' for char in text):
        return "Russian"
    
    # Check for German special characters
    if any(char in 'äöüßÄÖÜ' for char in text):
        return "German"
    
    # Common German words (expanded list for better detection)
    german_indicators = [
        'ist', 'was', 'wie', 'der', 'die', 'das', 'und', 'mit', 'von', 
        'für', 'auf', 'bei', 'nach', 'über', 'können', 'haben', 'sein',
        'werden', 'nicht', 'ich', 'sie', 'wir', 'ihr', 'mir', 'dir'
    ]
    
    # Common Russian words (transliterated)
    russian_indicators = [
        'что', 'как', 'где', 'когда', 'почему', 'это', 'для', 'или',
        'так', 'уже', 'если', 'все', 'его', 'они', 'мы', 'вы'
    ]
    
    # Count word matches
    words = text_lower.split()
    german_count = sum(1 for word in words if word in german_indicators)
    russian_count = sum(1 for word in words if word in russian_indicators)
    
    if german_count > 0:
        return "German"
    if russian_count > 0:
        return "Russian"
    
    # Default to English
    return "English"


def is_translation_request(text: str) -> tuple[bool, Optional[str]]:
    """
    Check if text contains explicit translation request.
    
    Args:
        text: User input text
        
    Returns:
        Tuple of (is_translation_request, target_language)
    """
    text_lower = text.lower()
    
    translation_patterns = {
        "Russian": [
            "переведи на русский", "перевести на русский", 
            "translate to russian", "на русском"
        ],
        "German": [
            "переведи на немецкий", "перевести на немецкий",
            "translate to german", "auf deutsch", "на немецком"
        ],
        "English": [
            "переведи на английский", "перевести на английский",
            "translate to english", "in english", "на английском"
        ]
    }
    
    for language, patterns in translation_patterns.items():
        if any(pattern in text_lower for pattern in patterns):
            return True, language
    
    return False, None


def is_course_mode_trigger(text: str) -> bool:
    """
    Check if text triggers course mode.
    
    Args:
        text: User input text
        
    Returns:
        True if course mode should be activated
    """
    text_lower = text.lower()
    
    course_triggers = [
        "курс", "course", "презентация", "presentation",
        "урок", "lesson", "модуль", "module", "обучение",
        "training", "правило", "rule", "из курса", "from course"
    ]
    
    return any(trigger in text_lower for trigger in course_triggers)


def is_course_mode_exit(text: str) -> bool:
    """
    Check if text indicates exiting course mode.
    
    Args:
        text: User input text
        
    Returns:
        True if course mode should be deactivated
    """
    text_lower = text.lower()
    
    exit_triggers = [
        "про рынок", "про налоги", "про объекты", "market",
        "tax", "property", "вне курса", "другая тема", 
        "сменим тему", "switch topic", "new topic"
    ]
    
    return any(trigger in text_lower for trigger in exit_triggers)
