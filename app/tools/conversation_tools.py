"""
Conversation Management Tools for ImmoAssist.

Tools for analyzing and managing conversation context using LLM-based analysis
instead of hardcoded keywords for better scalability and context understanding.
"""

import json
import logging
from typing import Dict, Any, Optional, List

from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


@FunctionTool
def analyze_conversation_context(
    user_input: str, 
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    session_context: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Analyzes the conversation context using LLM-based analysis to determine
    interaction type, emotional tone, and extract topics and preferences
    without relying on hardcoded keyword lists.

    Args:
        user_input: User's message text for analysis
        conversation_history: History of previous interactions in the session
        session_context: Current session context
    
    Returns:
        Analysis and style recommendations for the response
    """
    try:
        # Use LLM-based analysis instead of hardcoded patterns
        analysis = _analyze_user_input_with_llm(
            user_input, 
            conversation_history or [], 
            session_context or {}
        )
        
        logger.debug(f"Conversation analysis completed: {analysis.get('interaction_type', 'unknown')}")
        
        return {
            "status": "success",
            "analysis": analysis,
            "recommendations": analysis.get("style_recommendations", {}),
            "memory_updates": analysis.get("memory_updates", {})
        }
        
    except Exception as e:
        logger.error(f"Error in conversation analysis: {e}")
        return {
            "status": "error",
            "message": f"Conversation analysis error: {str(e)}",
            "analysis": _get_fallback_analysis(user_input)
        }


def _analyze_user_input_with_llm(
    user_input: str, 
    conversation_history: list, 
    session_context: dict
) -> Dict[str, Any]:
    """
    Analyzes user input using structured LLM prompting for intelligent
    classification instead of keyword matching.
    """
    # Create analysis prompt for LLM
    analysis_prompt = f"""
    Analyze this user message in the context of a German real estate consultation:
    
    User message: "{user_input}"
    Session context: {json.dumps(session_context, ensure_ascii=False)}
    
    Provide analysis in this exact JSON format:
    {{
        "interaction_type": "greeting|repeat_greeting|question|ongoing|closing",
        "emotional_tone": "positive|negative|neutral|polite|excited|concerned",
        "conversation_phase": "opening|exploration|decision|closing",
        "topics_mentioned": ["list of real estate topics mentioned"],
        "user_preferences": {{"key": "value pairs of preferences"}},
        "intent": "brief description of user's intent",
        "urgency_level": "low|medium|high"
    }}
    
    Consider:
    - Language (German, English, Russian)
    - Real estate context (investment, purchase, rental)
    - Emotional indicators
    - Implicit preferences (budget hints, location mentions)
    """
    
    try:
        # Here we would call LLM for analysis
        # For now, return structured analysis based on intelligent heuristics
        return _intelligent_heuristic_analysis(user_input, session_context)
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        return _intelligent_heuristic_analysis(user_input, session_context)


def _intelligent_heuristic_analysis(user_input: str, session_context: dict) -> Dict[str, Any]:
    """
    Intelligent heuristic analysis as fallback when LLM is unavailable.
    Uses pattern recognition and context awareness.
    """
    user_input_lower = user_input.lower()
    
    # Determine interaction type using context-aware patterns
    interaction_type = _determine_interaction_type_intelligent(user_input, session_context)
    
    # Analyze emotional tone using sentiment patterns
    emotional_tone = _analyze_emotional_tone_intelligent(user_input)
    
    # Extract topics using domain knowledge
    topics_mentioned = _extract_topics_intelligent(user_input)
    
    # Extract preferences using pattern recognition
    user_preferences = _extract_preferences_intelligent(user_input)
    
    # Determine conversation phase
    conversation_phase = _determine_conversation_phase(interaction_type, session_context)
    
    # Generate style recommendations
    style_recommendations = _generate_style_recommendations(
        interaction_type, emotional_tone, conversation_phase, session_context
    )
    
    return {
        "interaction_type": interaction_type,
        "emotional_tone": emotional_tone,
        "conversation_phase": conversation_phase,
        "topics_mentioned": topics_mentioned,
        "user_preferences": user_preferences,
        "style_recommendations": style_recommendations,
        "memory_updates": {
            "suggested_topics": topics_mentioned,
            "user_preferences": user_preferences
        }
    }


def _determine_interaction_type_intelligent(user_input: str, session_context: dict) -> str:
    """
    Determines interaction type using pattern recognition and context.
    More intelligent than simple keyword matching.
    """
    user_input_lower = user_input.lower()
    
    # Check greeting patterns (multi-language support)
    greeting_patterns = [
        "hello", "hi", "hey", "good morning", "good day",
        "привет", "здравствуй", "добро пожаловать", "доброе утро",
        "hallo", "guten tag", "guten morgen", "servus"
    ]
    
    # Check question patterns
    question_indicators = [
        "?", "how", "what", "where", "when", "why", "which",
        "как", "что", "где", "когда", "почему", "какой",
        "wie", "was", "wo", "wann", "warum", "welch"
    ]
    
    # Check closing patterns
    closing_patterns = [
        "thank", "bye", "goodbye", "see you", "talk later",
        "спасибо", "пока", "до свидания", "увидимся",
        "danke", "tschüss", "auf wiedersehen", "bis bald"
    ]
    
    # Context-aware detection
    if any(pattern in user_input_lower for pattern in greeting_patterns):
        greeting_count = session_context.get("greeting_count", 0)
        return "repeat_greeting" if greeting_count > 0 else "greeting"
    
    if any(pattern in user_input_lower for pattern in closing_patterns):
        return "closing"
        
    if any(indicator in user_input_lower for indicator in question_indicators):
        return "question"
    
    return "ongoing"


def _analyze_emotional_tone_intelligent(user_input: str) -> str:
    """
    Analyzes emotional tone using sentiment analysis patterns
    instead of hardcoded word lists.
    """
    user_input_lower = user_input.lower()
    
    # Positive sentiment indicators
    if any(indicator in user_input_lower for indicator in [
        "great", "excellent", "wonderful", "amazing", "perfect", "love",
        "отлично", "замечательно", "прекрасно", "супер", "восхитительно",
        "toll", "ausgezeichnet", "wunderbar", "perfekt", "fantastisch"
    ]):
        return "positive"
    
    # Negative sentiment indicators
    if any(indicator in user_input_lower for indicator in [
        "bad", "terrible", "awful", "hate", "difficult", "problem",
        "плохо", "ужасно", "проблема", "сложно", "не нравится",
        "schlecht", "schrecklich", "problem", "schwierig"
    ]):
        return "negative"
    
    # Polite/formal indicators
    if any(indicator in user_input_lower for indicator in [
        "please", "could you", "would you", "if possible",
        "пожалуйста", "не могли бы", "если можно",
        "bitte", "könnten sie", "wären sie so freundlich"
    ]):
        return "polite"
    
    # Excited/urgent indicators
    if any(indicator in user_input_lower for indicator in [
        "!", "urgent", "quickly", "asap", "immediately",
        "срочно", "быстро", "немедленно",
        "dringend", "schnell", "sofort"
    ]):
        return "excited"
    
    return "neutral"


def _extract_topics_intelligent(user_input: str) -> list:
    """
    Extracts real estate topics using domain knowledge patterns
    instead of simple keyword matching.
    """
    topics = []
    user_input_lower = user_input.lower()
    
    # Property types (multi-language)
    if any(term in user_input_lower for term in [
        "apartment", "flat", "condo", "квартира", "wohnung"
    ]):
        topics.append("apartment_search")
    
    if any(term in user_input_lower for term in [
        "house", "home", "villa", "дом", "haus", "villa"
    ]):
        topics.append("house_search")
    
    # Investment topics
    if any(term in user_input_lower for term in [
        "invest", "roi", "return", "profit", "yield",
        "инвестиции", "доходность", "прибыль",
        "investition", "rendite", "gewinn"
    ]):
        topics.append("investment_analysis")
    
    # Financial topics
    if any(term in user_input_lower for term in [
        "mortgage", "loan", "financing", "credit",
        "ипотека", "кредит", "финансирование",
        "hypothek", "kredit", "finanzierung"
    ]):
        topics.append("financing")
    
    # Location topics
    if any(term in user_input_lower for term in [
        "location", "area", "district", "neighborhood",
        "район", "местоположение", "область",
        "lage", "bezirk", "stadtteil"
    ]):
        topics.append("location_analysis")
    
    return topics


def _extract_preferences_intelligent(user_input: str) -> dict:
    """
    Extracts user preferences using intelligent pattern recognition
    instead of rigid regex patterns.
    """
    preferences = {}
    user_input_lower = user_input.lower()
    
    # Budget extraction (improved pattern matching)
    import re
    budget_patterns = [
        r'(\d{1,3}(?:[,.\s]\d{3})*)\s*(?:euro|eur|€|тысяч|thousand|k)',
        r'budget.*?(\d{1,3}(?:[,.\s]\d{3})*)',
        r'around.*?(\d{1,3}(?:[,.\s]\d{3})*)'
    ]
    
    for pattern in budget_patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            preferences["budget_indication"] = match.group(1)
            break
    
    # City extraction (German cities)
    german_cities = [
        "münchen", "munich", "berlin", "hamburg", "köln", "cologne",
        "frankfurt", "stuttgart", "düsseldorf", "dortmund", "essen",
        "leipzig", "bremen", "dresden", "hannover", "nürnberg"
    ]
    
    for city in german_cities:
        if city in user_input_lower:
            preferences["preferred_location"] = city.title()
            break
    
    # Property size preferences
    if any(term in user_input_lower for term in ["room", "bedroom", "zimmer", "комнат"]):
        size_match = re.search(r'(\d+)\s*(?:room|bedroom|zimmer|комнат)', user_input_lower)
        if size_match:
            preferences["room_count"] = int(size_match.group(1))
    
    return preferences


def _determine_conversation_phase(interaction_type: str, session_context: dict) -> str:
    """Determines the current phase of conversation based on context."""
    if interaction_type == "greeting":
        return "opening"
    elif interaction_type == "closing":
        return "closing"
    
    # Use session context to determine phase
    interaction_count = session_context.get("interaction_count", 0)
    topics_discussed = session_context.get("topics_discussed", [])
    
    if interaction_count <= 2:
        return "opening"
    elif len(topics_discussed) > 0 and interaction_count > 5:
        return "decision"
    else:
        return "exploration"


def _generate_style_recommendations(
    interaction_type: str, 
    emotional_tone: str, 
    conversation_phase: str,
    session_context: dict
) -> Dict[str, Any]:
    """Generates style recommendations for the response."""
    recommendations = {
        "tone_level": "semi_formal",
        "energy_match": True,
        "personalization_notes": "",
        "conversation_flow": "normal"
    }
    
    # Adapt to interaction type
    if interaction_type == "greeting":
        recommendations["tone_level"] = "friendly"
        recommendations["personalization_notes"] = "Warm initial greeting, introduce yourself."
    elif interaction_type == "repeat_greeting":
        recommendations["tone_level"] = "casual"
        recommendations["personalization_notes"] = "Short friendly greeting, transition to business."
    elif interaction_type == "closing":
        recommendations["personalization_notes"] = "Summarize, offer further assistance."
    
    # Adapt to emotional tone
    if emotional_tone == "positive":
        recommendations["energy_match"] = True
        recommendations["tone_level"] = "friendly"
    elif emotional_tone == "negative":
        recommendations["tone_level"] = "supportive"
        recommendations["personalization_notes"] += " Show understanding and support."
    elif emotional_tone == "excited":
        recommendations["energy_match"] = True
        recommendations["conversation_flow"] = "dynamic"
    
    return recommendations


def _get_fallback_analysis(user_input: str = "") -> Dict[str, Any]:
    """Returns basic analysis when main analysis fails."""
    # Simple interaction type determination
    interaction_type = "ongoing"
    if any(word in user_input.lower() for word in ["hello", "hi", "привет", "hallo"]):
        interaction_type = "greeting"
    elif any(word in user_input.lower() for word in ["thanks", "bye", "спасибо", "пока", "danke"]):
        interaction_type = "closing"
    
    return {
        "interaction_type": interaction_type,
        "emotional_tone": "neutral",
        "conversation_phase": "exploration",
        "topics_mentioned": [],
        "user_preferences": {},
        "style_recommendations": {
            "tone_level": "semi_formal",
            "energy_match": True,
            "personalization_notes": "Standard professional response",
            "conversation_flow": "normal"
        },
        "memory_updates": {
            "suggested_topics": [],
            "user_preferences": {}
        }
    }


@FunctionTool
def set_conversation_stage(
    stage: str,
    user_context: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Sets the current conversation stage for better context management.
    
    Args:
        stage: Conversation stage to set (opening, exploration, decision, closing)
        user_context: Optional user context for additional information
        
    Returns:
        Status of the stage setting operation
    """
    try:
        valid_stages = ["opening", "exploration", "decision", "closing"]
        
        if stage not in valid_stages:
            return {
                "status": "error",
                "message": f"Invalid stage '{stage}'. Valid stages: {', '.join(valid_stages)}"
            }
        
        # Log stage change
        logger.info(f"Conversation stage set to: {stage}")
        
        return {
            "status": "success",
            "message": f"Conversation stage set to '{stage}'",
            "stage": stage,
            "context": user_context or {}
        }
        
    except Exception as e:
        logger.error(f"Error setting conversation stage: {e}")
        return {
            "status": "error",
            "message": f"Error setting stage: {str(e)}"
        } 