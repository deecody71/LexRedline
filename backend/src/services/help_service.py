"""Help service that answers general questions about LexRedline using OpenAI + built-in FAQ."""

import os
from typing import Dict, Any, List

# Built-in FAQ knowledge base
FAQ = [
    {
        "question": "What is LexRedline?",
        "answer": "LexRedline is an AI-powered contract review engine that scans contracts, "
                  "flags risky clauses, and suggests redlines in minutes instead of days."
    },
    {
        "question": "How do I upload a contract?",
        "answer": "Go to the Upload page, select a PDF or DOCX file from your computer, "
                  "optionally add expectations about what you want to see in the contract, "
                  "and click 'Analyze'. The analysis takes just seconds."
    },
    {
        "question": "What file formats are supported?",
        "answer": "LexRedline supports PDF (.pdf), Word (.docx), and plain text files. "
                  "PDF files are parsed using PyMuPDF, and DOCX files using python-docx."
    },
    {
        "question": "What clause types can be detected?",
        "answer": "The engine detects 33+ clause types including: Indemnification, "
                  "Limitation of Liability, Governing Law, Confidentiality, Termination, "
                  "Non-Compete, Force Majeure, Warranty, Assignment, Entire Agreement, "
                  "Intellectual Property, Data Protection, Payment Terms, and many more."
    },
    {
        "question": "How is risk scored?",
        "answer": "Each clause is scored using a legal rubric with 4 risk levels: "
                  "LOW (standard language), MEDIUM (moderate concerns), HIGH (aggressive language), "
                  "and CRITICAL (highly one-sided or risky). The overall contract risk is a "
                  "weighted average of all clause scores."
    },
    {
        "question": "What are redline suggestions?",
        "answer": "Redline suggestions are market-standard alternative language for flagged clauses. "
                  "They help you negotiate better terms by providing concrete replacement text "
                  "for aggressive or one-sided clauses."
    },
    {
        "question": "Can I save my analysis results?",
        "answer": "Yes! If you're signed in with Clerk authentication, your analysis results "
                  "are automatically saved to your account. You can view your history on the "
                  "Dashboard page and revisit any previous analysis."
    },
    {
        "question": "What are profile preferences?",
        "answer": "Profile preferences let you customize how the engine analyzes contracts. "
                  "You can select preferences like 'Liability & Financial Caps' or 'Data Privacy' "
                  "to make the engine focus on specific risk areas that matter to you."
    },
    {
        "question": "What are contract expectations?",
        "answer": "Expectations are free-form notes about what you want to see in a contract. "
                  "For example, you can type 'I need 30-day termination for convenience' and "
                  "the engine will check if the contract includes that clause."
    },
    {
        "question": "Is my data secure?",
        "answer": "Yes. Contracts are stored per-user with strict ownership verification. "
                  "API endpoints use Clerk JWT authentication. Only the contract owner can "
                  "access their analysis results."
    },
    {
        "question": "How do I create an account?",
        "answer": "Click 'Sign Up' on the login page. You can sign up with Google OAuth "
                  "or email and password via Clerk authentication."
    },
    {
        "question": "What does the risk score number mean?",
        "answer": "The risk score is a number from 0.0 to 1.0. LOW risk is below 0.25, "
                  "MEDIUM is 0.25-0.45, HIGH is 0.45-0.70, and CRITICAL is above 0.70. "
                  "Higher scores indicate more aggressive or one-sided terms."
    },
    {
        "question": "Can I use LexRedline for free?",
        "answer": "LexRedline is currently in development. Please contact the team for "
                  "pricing and availability information."
    },
    {
        "question": "What is the difference between reviewer and creator profiles?",
        "answer": "Reviewer profiles focus on identifying risks in contracts you're reviewing "
                  "from another party. Creator profiles help you check your own contracts for "
                  "market-standard language and potential negotiation friction points."
    },
    {
        "question": "How long does analysis take?",
        "answer": "The pattern-based engine analyzes typical contracts in 3-10 milliseconds. "
                  "Even large contracts with 50+ pages complete in under a second."
    },
    {
        "question": "What if I find a bug or have a feature request?",
        "answer": "Please contact the LexRedline team through the project's GitHub repository "
                  "or reach out to the development team directly."
    },
    {
        "question": "How does the expectations matching work?",
        "answer": "The engine uses keyword matching to parse your expectations text. "
                  "For example, typing 'indemnification' maps to the Indemnification clause type. "
                  "It then compares your expectations against the detected clauses and calculates "
                  "a match percentage, showing what's covered and what's missing."
    },
    {
        "question": "What is the Q&A feature?",
        "answer": "The Q&A feature lets you ask questions about your contract analysis results. "
                  "For example, 'Why is the limitation of liability scored as high risk?' "
                  "The AI assistant answers based on the analysis data. Requires an OpenAI API key."
    },
]

HELP_SYSTEM_PROMPT = """You are a helpful assistant for LexRedline, an AI-powered contract review tool.
Answer user questions about how to use the platform, what features are available,
and how the analysis works.

You have access to a built-in FAQ that you can use as a reference.
If the user's question is not covered by the FAQ, use your general knowledge
to provide a helpful answer. Be concise and specific."""


def get_openai_client():
    """Get OpenAI client if API key is configured."""
    from openai import OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def search_faq(query: str) -> List[Dict[str, str]]:
    """Search the built-in FAQ for relevant answers using keyword matching."""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    results = []

    for item in FAQ:
        q_lower = item["question"].lower()
        # Count matching words
        q_words = set(q_lower.split())
        overlap = len(query_words & q_words)
        # Also check if query is a substring of the question
        substring_match = any(word in q_lower for word in query_words if len(word) > 3)

        if overlap > 0 or substring_match:
            score = overlap + (2 if substring_match else 0)
            results.append({
                "question": item["question"],
                "answer": item["answer"],
                "relevance": score,
            })

    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:3]


async def get_help(question: str) -> Dict[str, Any]:
    """
    Answer a general help question about LexRedline.
    
    First searches the built-in FAQ, then falls back to OpenAI if needed.
    
    Args:
        question: The user's help question.
    
    Returns:
        Dict with 'answer' and 'source' keys.
    """
    # First, try the FAQ
    faq_results = search_faq(question)
    if faq_results:
        best = faq_results[0]
        return {
            "answer": best["answer"],
            "source": "faq",
            "related_questions": [r["question"] for r in faq_results[1:]],
        }

    # Fall back to OpenAI
    client = get_openai_client()
    if client is None:
        return {
            "answer": "I couldn't find a direct answer in the FAQ. "
                     "The AI help feature requires an OpenAI API key. "
                     "Please set the OPENAI_API_KEY environment variable to enable it.",
            "source": None,
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": HELP_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            max_tokens=500,
            temperature=0.3,
        )

        answer = response.choices[0].message.content.strip()
        return {
            "answer": answer,
            "source": "openai",
            "model_used": "gpt-4o-mini",
        }

    except Exception as e:
        return {
            "answer": f"Sorry, I encountered an error: {str(e)}",
            "source": None,
            "error": str(e),
        }