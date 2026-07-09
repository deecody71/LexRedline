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
    result = await answer_question(request.question, None)
    return QAResponse(answer=result["answer"], model_used=result.get("model_used"))


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
    """
    result = await get_help(request.question)
    return HelpResponse(
        answer=result["answer"],
        source=result.get("source"),
        related_questions=result.get("related_questions", []),
        model_used=result.get("model_used"),
    )