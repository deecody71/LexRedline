"""FastAPI routes for the LexRedline contract analysis API."""

import os
import uuid
import tempfile
from typing import Optional, List

from fastapi import APIRouter, UploadFile, File, HTTPException, Body

from src.models import (
    Contract, ClauseType, RiskLevel,
    AnalysisResult, Clause
)
from src.api.schemas import (
    AnalyzeTextRequest,
    AnalysisResultResponse,
    ErrorResponse,
    HealthResponse,
    ModelInfo,
    ClauseTypeInfo,
    SectionSchema,
    ClauseSchema,
    RiskScoreSchema,
    RedlineSuggestionSchema,
)
from src.parsers import parse_contract, parse_contract_bytes
from src.analysis import ContractAnalyzer

router = APIRouter()

# Global analyzer instance (reused across requests)
analyzer = ContractAnalyzer()

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc'}

# Maximum upload size: 50MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024


def _result_to_response(result: AnalysisResult, job_id: str = "") -> AnalysisResultResponse:
    """Convert an AnalysisResult to the response schema."""
    return AnalysisResultResponse(
        job_id=job_id,
        filename=result.contract.filename,
        file_type=result.contract.file_type,
        page_count=result.contract.page_count,
        sections=_sections_to_schema(result.contract.sections),
        full_text=result.contract.full_text[:10000],  # Truncate for API responses
        clauses=[ClauseSchema(
            clause_type=c.clause_type,
            section_ref=c.section_ref,
            text=c.text[:1000],
            confidence=c.confidence,
            metadata=c.metadata,
        ) for c in result.clauses],
        risk_scores=[RiskScoreSchema(
            clause_type=rs.clause_type,
            risk_level=rs.risk_level,
            score=rs.score,
            reasoning=rs.reasoning,
            flags=rs.flags,
        ) for rs in result.risk_scores],
        overall_risk=result.overall_risk,
        overall_risk_score=result.overall_risk_score,
        redlines=[RedlineSuggestionSchema(
            clause_type=r.clause_type,
            original_text=r.original_text[:500],
            suggested_text=r.suggested_text,
            risk_reason=r.risk_reason,
            priority=r.priority,
        ) for r in result.redlines],
        clause_count=result.clause_count,
        analysis_time_ms=result.analysis_time_ms,
        contract_metadata=result.contract.metadata,
        parsed_at=result.contract.parsed_at.isoformat() if result.contract.parsed_at else None,
    )


def _sections_to_schema(sections):
    """Convert Section list to schema recursively."""
    return [SectionSchema(
        heading=s.heading,
        level=s.level,
        content=s.content,
        subsections=_sections_to_schema(s.subsections),
        start_page=s.start_page,
        end_page=s.end_page,
    ) for s in sections]


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@router.get("/models", response_model=ModelInfo, tags=["System"])
async def get_model_info():
    """Get information about the analysis model and supported clause types."""
    clause_types = []
    for ct in ClauseType:
        if ct == ClauseType.UNKNOWN:
            continue
        keywords = analyzer.detector.CLAUSE_PATTERNS.get(ct, {}).get("keywords", [])
        clause_types.append(ClauseTypeInfo(
            type=ct,
            description=f"Detection of {ct.value} clauses in contracts",
            keywords=keywords[:5],  # Top 5 keywords
        ))

    return ModelInfo(
        name="LexRedline Clause Detector v1",
        version="1.0.0",
        description="Pattern-based clause detection engine for commercial contracts",
        supported_clause_types=clause_types,
    )


@router.post(
    "/analyze/file",
    response_model=AnalysisResultResponse,
    responses={400: {"model": ErrorResponse}, 415: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
    tags=["Analysis"]
)
async def analyze_file(file: UploadFile = File(...)):
    """
    Upload and analyze a contract file (PDF or DOCX).

    Returns detected clauses, risk scores, and redline suggestions.
    """
    # Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if not ext or ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file format '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # Read file content
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024*1024)}MB."
        )

    job_id = str(uuid.uuid4())[:8]

    try:
        contract = parse_contract_bytes(content, file.filename or "contract")
        result = analyzer.analyze(contract)
        return _result_to_response(result, job_id=job_id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post(
    "/analyze/text",
    response_model=AnalysisResultResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["Analysis"]
)
async def analyze_text(request: AnalyzeTextRequest):
    """
    Analyze contract text directly (without file upload).

    Creates a temporary text-based contract and runs full analysis.
    """
    job_id = str(uuid.uuid4())[:8]

    try:
        # Build a simple Contract from text
        contract = Contract(
            filename=request.filename,
            file_type="txt",
            full_text=request.text,
            sections=[],  # Text input has no structured sections by default
            metadata={"source": "direct_text_input"}
        )

        result = analyzer.analyze(contract)
        return _result_to_response(result, job_id=job_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get(
    "/analyze/result/{job_id}",
    response_model=AnalysisResultResponse,
    tags=["Analysis"]
)
async def get_analysis_result(job_id: str):
    """
    Get analysis result by job ID.

    Note: Currently runs analysis on demand. In production, results
    would be cached or persisted.
    """
    raise HTTPException(
        status_code=501,
        detail="Result persistence not yet implemented. Use POST /analyze/file instead."
    )


@router.get(
    "/clauses",
    response_model=List[ClauseTypeInfo],
    tags=["Information"]
)
async def list_clause_types():
    """List all supported clause types and their keywords."""
    clause_types = []
    for ct in ClauseType:
        if ct == ClauseType.UNKNOWN:
            continue
        keywords = analyzer.detector.CLAUSE_PATTERNS.get(ct, {}).get("keywords", [])
        clause_types.append(ClauseTypeInfo(
            type=ct,
            description=f"Detection of {ct.value.replace('_', ' ').title()} clauses",
            keywords=keywords[:8],
        ))
    return clause_types