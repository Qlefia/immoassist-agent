"""
Session management service for ImmoAssist enterprise system.

This service handles user sessions, conversation state, and context management
following enterprise patterns with proper error handling and logging.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from ..config import config
from ..models.user import UserSession, ConversationHistory, UserInteraction


logger = logging.getLogger(__name__)


class SessionService:
    """
    Enterprise session management service.
    
    Handles session lifecycle, state persistence, and conversation history
    with support for multiple storage backends (memory, Redis, database).
    """
    
    def __init__(self):
        """Initialize session service with configuration."""
        self._sessions: Dict[str, UserSession] = {}
        self._histories: Dict[str, ConversationHistory] = {}
        self._session_timeout = timedelta(minutes=config.session_timeout_minutes)
        
        logger.info(f"SessionService initialized with {config.session_timeout_minutes}min timeout")
    
    def create_session(
        self, 
        user_id: Optional[str] = None,
        language: str = "de",
        initial_context: Optional[Dict] = None
    ) -> UserSession:
        """
        Create a new user session.
        
        Args:
            user_id: Optional user identifier
            language: Session language (de, en, ru)
            initial_context: Initial session context
            
        Returns:
            Created UserSession object
        """
        session_id = str(uuid4())
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            language=language,
            context=initial_context or {}
        )
        
        # Store session
        self._sessions[session_id] = session
        
        # Initialize conversation history
        self._histories[session_id] = ConversationHistory(
            session_id=session_id
        )
        
        logger.info(f"Created session {session_id} for user {user_id or 'anonymous'}")
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Retrieve session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            UserSession if found and valid, None otherwise
        """
        if session_id not in self._sessions:
            logger.warning(f"Session {session_id} not found")
            return None
        
        session = self._sessions[session_id]
        
        # Check if session is expired
        if self._is_session_expired(session):
            logger.info(f"Session {session_id} expired, removing")
            self._cleanup_session(session_id)
            return None
        
        # Update last activity
        updated_session = session.copy(update={
            "last_activity": datetime.now()
        })
        self._sessions[session_id] = updated_session
        
        return updated_session
    
    def update_session_context(
        self, 
        session_id: str, 
        context_updates: Dict
    ) -> bool:
        """
        Update session context.
        
        Args:
            session_id: Session identifier
            context_updates: Context data to merge
            
        Returns:
            True if updated successfully, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Merge context
        new_context = {**session.context, **context_updates}
        
        updated_session = session.copy(update={
            "context": new_context,
            "last_activity": datetime.now()
        })
        
        self._sessions[session_id] = updated_session
        logger.debug(f"Updated context for session {session_id}")
        return True
    
    def add_interaction(
        self,
        session_id: str,
        user_input: str,
        agent_response: str,
        agent_name: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add user interaction to conversation history.
        
        Args:
            session_id: Session identifier
            user_input: User's input message
            agent_response: Agent's response
            agent_name: Name of responding agent
            metadata: Additional interaction metadata
            
        Returns:
            True if added successfully, False otherwise
        """
        if session_id not in self._histories:
            logger.warning(f"No history found for session {session_id}")
            return False
        
        interaction = UserInteraction(
            session_id=session_id,
            user_input=user_input,
            agent_response=agent_response,
            agent_name=agent_name,
            metadata=metadata or {}
        )
        
        # Update conversation history
        history = self._histories[session_id]
        updated_interactions = history.interactions + [interaction]
        
        updated_history = history.copy(update={
            "interactions": updated_interactions,
            "total_interactions": len(updated_interactions)
        })
        
        self._histories[session_id] = updated_history
        
        logger.debug(f"Added interaction to session {session_id} history")
        return True
    
    def get_conversation_history(
        self, 
        session_id: str,
        last_n: Optional[int] = None
    ) -> Optional[ConversationHistory]:
        """
        Get conversation history for session.
        
        Args:
            session_id: Session identifier
            last_n: Optional number of recent interactions to return
            
        Returns:
            ConversationHistory if found, None otherwise
        """
        if session_id not in self._histories:
            return None
        
        history = self._histories[session_id]
        
        if last_n:
            # Return only last N interactions
            recent_interactions = history.interactions[-last_n:]
            history = history.copy(update={
                "interactions": recent_interactions
            })
        
        return history
    
    def end_session(self, session_id: str) -> bool:
        """
        End a session and cleanup resources.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if ended successfully, False otherwise
        """
        if session_id not in self._sessions:
            return False
        
        # TODO: Persist session data to permanent storage
        # await self._persist_session(session_id)
        
        self._cleanup_session(session_id)
        logger.info(f"Ended session {session_id}")
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self._cleanup_session(session_id)
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
    
    def get_session_stats(self) -> Dict:
        """
        Get session statistics.
        
        Returns:
            Dictionary with session statistics
        """
        total_sessions = len(self._sessions)
        active_sessions = sum(1 for s in self._sessions.values() if not self._is_session_expired(s))
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": total_sessions - active_sessions,
            "max_concurrent": config.max_concurrent_sessions
        }
    
    def _is_session_expired(self, session: UserSession) -> bool:
        """Check if session is expired."""
        return datetime.now() - session.last_activity > self._session_timeout
    
    def _cleanup_session(self, session_id: str) -> None:
        """Clean up session and related data."""
        # Remove from memory
        self._sessions.pop(session_id, None)
        
        # Clean up conversation history if not configured to persist
        if not config.enable_conversation_history:
            self._histories.pop(session_id, None) 