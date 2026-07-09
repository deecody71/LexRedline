"""Q&A service that answers user questions about contract analysis results using OpenAI."""

import os
from typing import Optional, Dict, Any

# System prompt for contract Q&A
QA_SYSTEM_PROMPT = """You are a contract analysis assistant for LexRedline, an AI-powered contract review tool.
You help users understand their contract analysis results.

The analysis result includes:
- Detected clauses (type, text, confidence)
- Risk scores per clause (low, medium, high, critical)
- Overall contract risk level
- Redline suggestions for improving clauses

Answer questions clearly and concisely based on the analysis data provided.
If you don't have enough information to answer, say so.
Focus on being helpful to legal professionals who are reviewing contracts."""


def get_openai_client():
    """Get OpenAI client if API key is configured."""
    from openai import OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


async def answer_question(question: str, analysis_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Answer a user question about a contract analysis result.
    
    Args:
        question: The user's question.
        analysis_result: Optional analysis result dict to provide context.
    
    Returns:
        Dict with 'answer' and 'model_used' keys.
    """
    client = get_openai_client()
    if client is None:
        return {
            "answer": "The AI Q&A feature requires an OpenAI API key. "
                     "Please set the OPENAI_API_KEY environment variable to enable this feature.",
            "model_used": None,
        }

    try:
        messages = [{"role": "system", "content": QA_SYSTEM_PROMPT}]

        # Add analysis context if provided
        if analysis_result:
            context = _format_analysis_context(analysis_result)
            messages.append({"role": "user", "content": f"Here is the contract analysis:\n\n{context}\n\nQuestion: {question}"})
        else:
            messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.3,
        )

        answer = response.choices[0].message.content.strip()
        return {
            "answer": answer,
            "model_used": "gpt-4o-mini",
        }

    except Exception as e:
        return {
            "answer": f"Sorry, I encountered an error processing your question: {str(e)}",
            "model_used": None,
            "error": str(e),
        }


def _format_analysis_context(analysis: Dict[str, Any]) -> str:
    """Format an analysis result dict into a readable context for the LLM."""
    lines = []
    lines.append(f"Contract: {analysis.get('filename', 'Unknown')}")
    lines.append(f"Overall Risk: {analysis.get('overall_risk', 'N/A')} ({analysis.get('overall_risk_score', 'N/A')})")
    lines.append(f"Clauses Detected: {analysis.get('clause_count', 0)}")
    lines.append("")

    # Add clauses
    clauses = analysis.get('clauses', [])
    risk_scores = analysis.get('risk_scores', [])
    redlines = analysis.get('redlines', [])

    lines.append("--- Detected Clauses ---")
    for i, clause in enumerate(clauses[:20]):  # Limit to 20 clauses
        ct = clause.get('clause_type', 'unknown')
        conf = clause.get('confidence', 0)
        # Find matching risk score
        risk_level = "unknown"
        for rs in risk_scores:
            if rs.get('clause_type') == ct:
                risk_level = rs.get('risk_level', 'unknown')
                break
        lines.append(f"  {i+1}. {ct} (confidence: {conf:.2f}, risk: {risk_level})")

    # Add redlines
    if redlines:
        lines.append("")
        lines.append("--- Redline Suggestions ---")
        for i, r in enumerate(redlines[:5]):
            lines.append(f"  {i+1}. [{r.get('priority', 'medium')}] {r.get('clause_type', 'unknown')}: {r.get('risk_reason', '')}")

    return "\n".join(lines)