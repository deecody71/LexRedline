"""FastAPI request/response schemas for the LexRedline API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from src.models import ClauseType, RiskLevel


# --- Request Schemas ---

class AnalyzeTextRequest(BaseModel):
    """Analyze a contract from raw text."""
    text: str = Field(..., min_length=1, description="Full contract text")
    filename: str = Field(default="contract.txt", description="Original filename for reference")


class AnalyzeFileResponse(BaseModel):
    """Response after parsing and starting analysis."""
    job_id: str = Field(..., description="Analysis job ID")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type")
    page_count: Optional[int] = Field(default=None, description="Number of pages")
    detected_clauses: int = Field(default=0, description="Number of clauses detected")
    status: str = Field(default="processing", description="Analysis status")


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