"""User profile model for preference-aware contract analysis."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile preferences that influence contract analysis.
    
    Profiles contain role (reviewer/creator/both) and selected preference IDs
    that affect clause detection priority, risk scoring sensitivity, and
    redline template selection.
    """
    role: str = Field(
        default="reviewer",
        description="User role: 'reviewer', 'creator', or 'both'"
    )
    preference_ids: List[str] = Field(
        default_factory=list,
        description="Selected preference IDs like 'liability_financial', 'data_privacy'"
    )
    custom_preferences: Optional[str] = Field(
        default=None,
        description="Free-text custom preferences for advanced users"
    )

    @property
    def is_active(self) -> bool:
        """Whether this profile has any active preferences."""
        return len(self.preference_ids) > 0 or bool(self.custom_preferences)