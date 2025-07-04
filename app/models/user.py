"""User domain models for ImmoAssist."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    """User preferences for property search and recommendations."""
    preferred_language: str = "de"
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    preferred_locations: List[str] = Field(default_factory=list)
    preferred_property_types: List[str] = Field(default_factory=list)
    min_rooms: Optional[int] = None
    max_rooms: Optional[int] = None
    
    class Config:
        frozen = True


class UserProfile(BaseModel):
    """User profile information."""
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    class Config:
        frozen = True


class UserSession(BaseModel):
    """User session for conversation state management."""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    language: str = "de"
    started_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    context: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    
    class Config:
        frozen = True


class UserInteraction(BaseModel):
    """Individual user interaction record."""
    interaction_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_input: str
    agent_response: str
    agent_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = True


class ConversationHistory(BaseModel):
    """Complete conversation history for a session."""
    session_id: str
    interactions: List[UserInteraction] = Field(default_factory=list)
    total_interactions: int = 0
    session_duration_minutes: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        frozen = True 