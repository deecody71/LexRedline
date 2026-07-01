# Data Models for LexRedline Contract Engine

"""
Pydantic models representing contracts, sections, clauses, and analysis results.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from src.models.profile import UserProfile


class ClauseType(str, Enum):
    """Standard clause types found in commercial contracts.
    
    Taxonomy aligned with the Legal Domain Specialist's classification.
    Covers 33+ clause types common across SaaS, NDA, PSA, and License agreements.
    """
    # Core commercial clauses
    INDEMNIFICATION = "indemnification"
    LIMITATION_OF_LIABILITY = "limitation_of_liability"
    GOVERNING_LAW = "governing_law"
    CONFIDENTIALITY = "confidentiality"
    NON_COMPETE = "non_compete"
    NON_SOLICITATION = "non_solicitation"
    FORCE_MAJEURE = "force_majeure"
    WARRANTY = "warranty"
    DISCLAIMER = "disclaimer"
    ASSIGNMENT = "assignment"
    ENTIRE_AGREEMENT = "entire_agreement"
    
    # Termination types
    TERMINATION_FOR_CONVENIENCE = "termination_for_convenience"
    TERMINATION_FOR_CAUSE = "termination_for_cause"
    TERMINATION_FOR_CHANGE_OF_CONTROL = "termination_for_change_of_control"
    SURVIVAL = "survival"
    
    # Dispute resolution
    DISPUTE_RESOLUTION_ARBITRATION = "dispute_resolution_arbitration"
    DISPUTE_RESOLUTION_MEDIATION = "dispute_resolution_mediation"
    DISPUTE_RESOLUTION_LITIGATION = "dispute_resolution_litigation"
    
    # IP and data
    INTELLECTUAL_PROPERTY = "intellectual_property"
    DATA_PROTECTION = "data_protection"
    
    # Payment and commercial
    PAYMENT_TERMS = "payment_terms"
    INTEREST_ON_LATE_PAYMENTS = "interest_on_late_payments"
    LIQUIDATED_DAMAGES = "liquidated_damages"
    EXCLUSIVITY = "exclusivity"
    MOST_FAVORED_NATION = "most_favored_nation"
    
    # Operational
    DELIVERABLES = "deliverables"
    AUDIT_RIGHTS = "audit_rights"
    INSURANCE = "insurance"
    SUBCONTRACTING = "subcontracting"
    PUBLICITY = "publicity"
    COMPLIANCE_WITH_LAWS = "compliance_with_laws"
    
    # Boilerplate
    NOTICE = "notice"
    WAIVER = "waiver"
    SEVERABILITY = "severability"
    COUNTERPARTS = "counterparts"
    ORDER_OF_PRECEDENCE = "order_of_precedence"
    
    # Legacy aliases (for backward compat)
    TERMINATION = "termination"  # Generic catch-all
    DISPUTE_RESOLUTION = "dispute_resolution"  # Generic catch-all
    NON_DISCLOSURE = "confidentiality"  # Alias
    
    # Generic / Other
    EXPENSES = "expenses"
    REPRESENTATIONS = "representations"
    COVENANTS = "covenants"
    DEFINITIONS = "definitions"
    SIGNATURES = "signatures"
    SCHEDULE = "schedule"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Section(BaseModel):
    """A section or subsection within a contract."""
    heading: str = Field(default="", description="Section heading text")
    level: int = Field(default=1, description="Heading level (1=top, 2=sub, etc.)")
    content: str = Field(default="", description="Section body text")
    subsections: List[Section] = Field(default_factory=list, description="Nested subsections")
    start_page: Optional[int] = Field(default=None, description="Starting page number")
    end_page: Optional[int] = Field(default=None, description="Ending page number")


class Clause(BaseModel):
    """A detected clause within a contract."""
    clause_type: ClauseType = Field(..., description="Type of clause detected")
    section_ref: Optional[str] = Field(default=None, description="Section number/heading")
    text: str = Field(..., description="The extracted clause text")
    start_char: int = Field(default=0, description="Character offset in full text")
    end_char: int = Field(default=0, description="End character offset")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Detection confidence")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Contract(BaseModel):
    """A parsed contract document."""
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File extension: pdf, docx, doc")
    full_text: str = Field(default="", description="Complete extracted text")
    sections: List[Section] = Field(default_factory=list, description="Document sections")
    page_count: Optional[int] = Field(default=None, description="Number of pages")
    parsed_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class RiskScore(BaseModel):
    """Risk assessment for a single clause."""
    clause_type: ClauseType
    risk_level: RiskLevel
    score: float = Field(..., ge=0.0, le=1.0, description="Numeric risk score (0=low risk, 1=high risk)")
    reasoning: str = Field(default="", description="Explanation of why this risk level was assigned")
    flags: List[str] = Field(default_factory=list, description="Specific risk flags raised")


class RedlineSuggestion(BaseModel):
    """A suggested redline edit for a clause."""
    clause_type: ClauseType
    original_text: str = Field(..., description="The original clause text")
    suggested_text: str = Field(..., description="The suggested replacement text")
    risk_reason: str = Field(default="", description="Why this change is suggested")
    priority: RiskLevel = Field(default=RiskLevel.MEDIUM, description="Priority of this redline")


class AnalysisResult(BaseModel):
    """Complete analysis result for a contract."""
    contract: Contract = Field(..., description="The parsed contract")
    clauses: List[Clause] = Field(default_factory=list, description="Detected clauses")
    risk_scores: List[RiskScore] = Field(default_factory=list, description="Per-clause risk scores")
    overall_risk: RiskLevel = Field(default=RiskLevel.LOW, description="Overall contract risk")
    overall_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    redlines: List[RedlineSuggestion] = Field(default_factory=list, description="Suggested redlines")
    clause_count: int = Field(default=0, description="Number of clauses detected")
    analysis_time_ms: float = Field(default=0.0, description="Time taken for analysis in ms")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional analysis metadata (profile info, etc.)")