"""FastAPI request/response schemas for the LexRedline API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from src.models import ClauseType, RiskLevel
from src.models.profile import UserProfile


# --- Request Schemas ---

class AnalyzeTextRequest(BaseModel):
    """Analyze a contract from raw text."""
    text: str = Field(..., min_length=1, description="Full contract text")
    filename: str = Field(default="contract.txt", description="Original filename for reference")
    profile: Optional[UserProfile] = Field(default=None, description="User profile preferences")
    expectations: Optional[str] = Field(default=None, description="Free-text expectations about the contract")


class AnalyzeFileResponse(BaseModel):
    """Response after parsing and starting analysis."""
    job_id: str = Field(..., description="Analysis job ID")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type")
    page_count: Optional[int] = Field(default=None, description="Number of pages")
    detected_clauses: int = Field(default=0, description="Number of clauses detected")
    status: str = Field(default="processing", description="Analysis status")
    profile_applied: Optional[str] = Field(default=None, description="Profile role applied")


# --- Response Schemas ---

class SectionSchema(BaseModel):
    """Serializable section model."""
    heading: str
    level: int
    content: str
    subsections: List["SectionSchema"] = Field(default_factory=list)
    start_page: Optional[int] = None
    end_page: Optional[int] = None


class ClauseSchema(BaseModel):
    """Serializable clause model."""
    clause_type: ClauseType
    section_ref: Optional[str] = None
    text: str
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RiskScoreSchema(BaseModel):
    """Serializable risk score model."""
    clause_type: ClauseType
    risk_level: RiskLevel
    score: float
    reasoning: str
    flags: List[str] = Field(default_factory=list)


class RedlineSuggestionSchema(BaseModel):
    """Serializable redline suggestion model."""
    clause_type: ClauseType
    original_text: str
    suggested_text: str
    risk_reason: str
    priority: RiskLevel


class ProfileInfo(BaseModel):
    """Profile information in analysis response."""
    applied: bool = Field(default=False, description="Whether a profile was applied")
    role: Optional[str] = Field(default=None, description="Profile role used")
    preferences: List[str] = Field(default_factory=list, description="Active preference IDs")
    modifications: List[str] = Field(default_factory=list, description="What the profile changed")


class ExpectationMatchResult(BaseModel):
    """Expectations matching result."""
    total_expectations: int = 0
    matched: List[Dict[str, Any]] = Field(default_factory=list)
    unmatched: List[Dict[str, Any]] = Field(default_factory=list)
    match_percentage: float = 100.0
    matched_types: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class AnalysisResultResponse(BaseModel):
    """Full analysis result response."""
    job_id: str = Field(default="", description="Analysis job ID")
    filename: str
    file_type: str
    page_count: Optional[int] = None
    sections: List[SectionSchema] = Field(default_factory=list)
    full_text: str = Field(default="", description="Full extracted text")
    clauses: List[ClauseSchema] = Field(default_factory=list)
    risk_scores: List[RiskScoreSchema] = Field(default_factory=list)
    overall_risk: RiskLevel
    overall_risk_score: float
    redlines: List[RedlineSuggestionSchema] = Field(default_factory=list)
    clause_count: int
    analysis_time_ms: float
    contract_metadata: Dict[str, Any] = Field(default_factory=dict)
    parsed_at: Optional[str] = None
    profile: Optional[ProfileInfo] = Field(default=None, description="Profile info if applied")
    expectation_match: Optional[ExpectationMatchResult] = Field(default=None, description="Expectations matching results")


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    error_code: str = Field(default="unknown_error")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0.0"
    engine: str = "LexRedline Contract Engine"


class ClauseTypeInfo(BaseModel):
    """Information about a supported clause type."""
    type: ClauseType
    description: str = ""
    keywords: List[str] = Field(default_factory=list)


class ModelInfo(BaseModel):
    """Model information."""
    name: str
    version: str
    description: str
    supported_clause_types: List[ClauseTypeInfo] = Field(default_factory=list)


class QARequest(BaseModel):
    """Q&A request."""
    question: str = Field(..., min_length=1, description="User's question about the analysis")
    analysis_id: Optional[str] = Field(default=None, description="Contract analysis ID to ask about")


class QAResponse(BaseModel):
    """Q&A response."""
    answer: str
    model_used: Optional[str] = None


class HelpRequest(BaseModel):
    """Help request."""
    question: str = Field(..., min_length=1, description="User's help question")


class HelpResponse(BaseModel):
    """Help response."""
    answer: str
    source: Optional[str] = None
    related_questions: List[str] = Field(default_factory=list)
    model_used: Optional[str] = None