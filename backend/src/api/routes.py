"""FastAPI routes for the LexRedline contract analysis API."""

import os
import uuid
import json as json_module
from typing import Optional, List, Dict

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends

from src.models import (
    Contract, ClauseType, RiskLevel,
    AnalysisResult, Clause, UserProfile
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
        ProfileInfo,
        ExpectationMatchResult,
        AnalyzeFileResponse,
        QARequest,
        QAResponse,
        HelpRequest,
        HelpResponse,
    )
from src.parsers import parse_contract_bytes
from src.analysis import ContractAnalyzer
from src.auth import get_current_user, get_optional_user
from src.storage import save_contract, get_user_contracts, get_contract, init_db
from src.services.qa_service import answer_question
from src.services.help_service import get_help

router = APIRouter()

# Initialize database on module load (gracefully skip if team-db not available)
try:
    init_db()
except Exception as e:
    print(f"Warning: Database initialization skipped ({e})")

# Global analyzer instance for non-profile requests
_default_analyzer = ContractAnalyzer()

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc'}
MAX_UPLOAD_SIZE = 50 * 1024 * 1024


def _result_to_response(result: AnalysisResult, job_id: str = "") -> AnalysisResultResponse:
    """Convert an AnalysisResult to the response schema, including profile info."""
    meta = result.metadata or {}

    # Extract profile info if it was applied
    profile_info = None
    if meta.get("profile_applied"):
        profile_info = ProfileInfo(
            applied=True,
            role=meta.get("profile_role"),
            preferences=meta.get("profile_preferences", []),
            modifications=meta.get("profile_modifications", []),
        )

    # Extract expectation match if present
    expectation_match = None
    em = meta.get("expectation_match")
    if em:
        expectation_match = ExpectationMatchResult(
            total_expectations=em.get("total", 0),
            matched=em.get("matched", []),
            unmatched=em.get("unmatched", []),
            match_percentage=em.get("match_pct", 100.0),
            matched_types=em.get("matched_types", []),
            recommendations=em.get("recommendations", []),
        )

    return AnalysisResultResponse(
        job_id=job_id,
        filename=result.contract.filename,
        file_type=result.contract.file_type,
        page_count=result.contract.page_count,
        sections=_sections_to_schema(result.contract.sections),
        full_text=result.contract.full_text[:10000],
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
        contract_metadata=result.contract.metadata or {},
        parsed_at=result.contract.parsed_at.isoformat() if result.contract.parsed_at else None,
        profile=profile_info,
        expectation_match=expectation_match,
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
        if ct in (ClauseType.UNKNOWN, ClauseType.TERMINATION, ClauseType.DISPUTE_RESOLUTION, ClauseType.NON_DISCLOSURE):
            continue
        keywords = _default_analyzer.detector.CLAUSE_PATTERNS.get(ct, {}).get("keywords", [])
        clause_types.append(ClauseTypeInfo(
            type=ct,
            description=f"Detection of {ct.value.replace('_', ' ').title()} clauses",
            keywords=keywords[:5],
        ))

    return ModelInfo(
        name="LexRedline Clause Detector v2",
        version="2.0.0",
        description="Pattern-based clause detection engine with profile-aware risk analysis",
        supported_clause_types=clause_types,
    )


@router.post(
    "/analyze/file",
    response_model=AnalysisResultResponse,
    responses={400: {"model": ErrorResponse}, 415: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
    tags=["Analysis"]
)
async def analyze_file(
    file: UploadFile = File(...),
    profile_role: Optional[str] = Form(default=None),
    profile_preference_ids: Optional[str] = Form(default=None),
    expectations: Optional[str] = Form(default=None),
    user_id: str = Depends(get_optional_user),
):
    """
    Upload and analyze a contract file (PDF or DOCX).
    
    Optionally accepts:
    - profile data: profile_role, profile_preference_ids
    - expectations: free-form text describing what the user expects in the contract
    
    If an Authorization header with a valid Clerk JWT is provided,
    the result is saved to the user's contract history.
    Returns detected clauses, risk scores, redline suggestions, and expectation match.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if not ext or ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file format '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024*1024)}MB."
        )

    job_id = str(uuid.uuid4())[:8]

    # Build profile if provided
    profile = None
    if profile_role:
        pref_ids = [p.strip() for p in (profile_preference_ids or "").split(",") if p.strip()]
        profile = UserProfile(role=profile_role, preference_ids=pref_ids)

    try:
        contract = parse_contract_bytes(content, file.filename or "contract")
        analyzer = ContractAnalyzer(profile=profile) if profile else _default_analyzer
        result = analyzer.analyze(contract, expectations=expectations)
        response = _result_to_response(result, job_id=job_id)

        # Save to DB if authenticated
        if user_id and user_id != "anonymous":
            result_dict = response.model_dump()
            save_contract(user_id, file.filename or "contract", result_dict)

        return response

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
async def analyze_text(
    request: AnalyzeTextRequest,
    user_id: str = Depends(get_optional_user),
):
    """
    Analyze contract text directly (without file upload).
    
    Accepts optional:
    - profile in the JSON body
    - expectations: free-form text describing what the user expects
    
    If an Authorization header with a valid Clerk JWT is provided,
    the result is saved to the user's contract history.
    Returns full analysis with clauses, risk scores, redlines, and expectation match.
    """
    job_id = str(uuid.uuid4())[:8]

    try:
        contract = Contract(
            filename=request.filename,
            file_type="txt",
            full_text=request.text,
            metadata={"source": "direct_text_input"}
        )

        analyzer = ContractAnalyzer(profile=request.profile) if request.profile else _default_analyzer
        result = analyzer.analyze(contract, expectations=request.expectations)
        response = _result_to_response(result, job_id=job_id)

        # Save to DB if authenticated
        if user_id and user_id != "anonymous":
            result_dict = response.model_dump()
            save_contract(user_id, request.filename, result_dict)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get(
    "/contracts",
    response_model=List[Dict],
    tags=["Storage"]
)
async def list_user_contracts(user_id: str = Depends(get_current_user)):
    """
    List all contracts for the authenticated user.
    
    Returns summary info (id, filename, created_at) for each contract.
    Requires authentication.
    """
    if user_id == "anonymous":
        raise HTTPException(status_code=401, detail="Authentication required.")

    contracts = get_user_contracts(user_id)
    return contracts


@router.get(
    "/contracts/{contract_id}",
    response_model=Dict,
    tags=["Storage"]
)
async def get_contract_by_id(
    contract_id: str,
    user_id: str = Depends(get_current_user),
):
    """
    Get a specific contract by ID (with ownership verification).
    
    Returns the full analysis result including clauses, risk scores, and redlines.
    Only accessible by the contract owner.
    """
    if user_id == "anonymous":
        raise HTTPException(status_code=401, detail="Authentication required.")

    contract = get_contract(contract_id, user_id)
    if contract is None:
        raise HTTPException(
            status_code=404,
            detail="Contract not found or access denied.",
        )

    return contract


@router.get(
    "/clauses",
    response_model=List[ClauseTypeInfo],
    tags=["Information"]
)
async def list_clause_types():
    """List all supported clause types and their keywords."""
    clause_types = []
    for ct in ClauseType:
        if ct in (ClauseType.UNKNOWN, ClauseType.TERMINATION, ClauseType.DISPUTE_RESOLUTION, ClauseType.NON_DISCLOSURE):
            continue
        keywords = _default_analyzer.detector.CLAUSE_PATTERNS.get(ct, {}).get("keywords", [])
        clause_types.append(ClauseTypeInfo(
            type=ct,
            description=f"Detection of {ct.value.replace('_', ' ').title()} clauses",
            keywords=keywords[:8],
        ))
    return clause_types


@router.get(
    "/profiles",
    tags=["Information"]
)
async def list_available_profiles():
    """List available profile preferences from the spec."""
    import json
    from pathlib import Path

    spec_path = Path("/home/team/shared/profile_preferences.json")
    if spec_path.exists():
        with open(spec_path) as f:
            spec = json.load(f)
        return {"available_profiles": spec}
    return {"available_profiles": None}


@router.post(
    "/qa",
    response_model=QAResponse,
    tags=["AI"]
)
async def ask_question(request: QARequest):
    """
    Ask a question about a contract analysis result.

    Requires OPENAI_API_KEY environment variable to be set.
    If analysis_id is provided, fetches the analysis context.
    Returns an AI-generated answer based on the analysis data.
    """
    analysis_result = None
    if request.analysis_id:
        try:
            contract = get_contract(request.analysis_id, user_id="system")
            if contract and "analysis" in contract:
                analysis_result = contract["analysis"]
        except Exception:
            pass

    result = await answer_question(request.question, analysis_result)
    return QAResponse(
        answer=result["answer"],
        model_used=result.get("model_used"),
    )


@router.post(
    "/help",
    response_model=HelpResponse,
    tags=["AI"]
)
async def get_help_answer(request: HelpRequest):
    """
    Get help about LexRedline features.

    First searches the built-in FAQ for matching answers.
    Falls back to OpenAI if no FAQ match is found.
    Returns the answer along with related questions.
    """
    result = await get_help(request.question)
    return HelpResponse(
        answer=result["answer"],
        source=result.get("source"),
        related_questions=result.get("related_questions"),
        model_used=result.get("model_used"),
    )