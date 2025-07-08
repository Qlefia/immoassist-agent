"""Property domain models for ImmoAssist."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class EnergyClass(str, Enum):
    """Energy efficiency classes for German properties."""

    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C = "C"


class PropertyType(str, Enum):
    """Types of properties available for investment."""

    APARTMENT = "apartment"
    HOUSE = "house"
    STUDIO = "studio"


class PropertyLocation(BaseModel):
    """Location details for a property."""

    city: str
    district: Optional[str] = None
    state: str
    postal_code: str
    address: Optional[str] = None

    class Config:
        frozen = True


class Property(BaseModel):
    """Complete property entity for German real estate investments."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    property_type: PropertyType
    location: PropertyLocation
    purchase_price: Decimal = Field(..., gt=0)
    size_sqm: Decimal = Field(..., gt=0)
    rooms: Decimal = Field(..., gt=0)
    energy_class: EnergyClass
    monthly_rental_income: Decimal = Field(..., gt=0)
    is_available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        frozen = True


class PropertySearchCriteria(BaseModel):
    """Search criteria for finding properties."""

    location: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    property_type: Optional[PropertyType] = None
    min_rooms: Optional[Decimal] = None
    max_rooms: Optional[Decimal] = None
    energy_classes: Optional[list[EnergyClass]] = None

    class Config:
        frozen = True


class PropertySearchResult(BaseModel):
    """Result container for property search operations."""

    properties: list[Property]
    total_count: int = Field(..., ge=0)
    search_criteria: PropertySearchCriteria
    search_timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        frozen = True
