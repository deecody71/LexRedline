# LexRedline Contract Engine — Architecture Document

## Overview

The LexRedline Contract Engine is the core AI/ML backend of the LexRedline platform. It accepts contract documents (PDF, DOCX, DOC), parses them into structured representations, detects legal clauses, scores them for risk, and generates redline suggestions.

## Architecture Diagram

```
┌─────────────┐     ┌────────────────┐     ┌─────────────────────┐
│  Upload/    │     │  Contract      │     │  Clause Detection   │
│  Text Input │────▶│  Parser        │────▶│  Engine             │
└─────────────┘     │  (PDF/DOCX)    │     │  (Pattern-based)    │
                     └────────────────┘     └─────────┬───────────┘
                                                        │
                     ┌────────────────┐     ┌───────────▼───────────┐
                     │  Redline       │◀───│  Risk Scoring         │
                     │  Generator     │     │  Engine               │
                     │  (Templates)   │     │  (Heuristic rules)    │
                     └───────┬────────┘     └───────────────────────┘
                             │
                     ┌───────▼────────┐
                     │  FastAPI REST  │
                     │  (Port 3000)   │
                     └────────────────┘
```

## Component Design

### 1. Contract Parser (`src/parsers/`)

Parse PDF (PyMuPDF) and DOCX (python-docx) files while preserving document structure.

**Key design decisions:**
- PyMuPDF over pdfplumber for speed and wider format support
- Heading detection via heuristics (numbered sections, ALL CAPS, section keywords)
- Section nesting tracked via a stack-based parser
- Both file-path and bytes-based parsing for API flexibility

**Interfaces:**
- `BaseParser` — abstract base class
- `PDFParser` — uses PyMuPDF, extracts text blocks with position info
- `DOCXParser` — uses python-docx, reads paragraph styles for structure
- `parse_contract()` / `parse_contract_bytes()` — unified entry points

### 2. Clause Detection (`src/analysis/clause_detector.py`)

Detects ~25 clause types using keyword spotting and regex patterns.

**Detection strategy:**
1. **Section heading matching** — if a section heading matches a known clause name (e.g., "Indemnification"), flag all content in that section
2. **Pattern scanning** — regex patterns search section content for keywords
3. **Full-text fallback** — scan entire text for clause patterns that span sections

**Supported clause types:**
| Type | Key Detection Keywords |
|------|----------------------|
| Indemnification | indemnify, hold harmless, defend |
| Limitation of Liability | cap, limitation, not exceed |
| Governing Law | governed by, choice of law, jurisdiction |
| Confidentiality | confidential, non-disclosure, proprietary |
| Termination | terminate, expiration, survival |
| Non-Compete | non-compete, restrictive covenant |
| Force Majeure | force majeure, act of God |
| Warranty | warrant, as-is, limited warranty |
| Disclaimer | disclaim, no warranty |
| Assignment | assign, successor, novation |
| Entire Agreement | entire agreement, merger, supersedes |
| Dispute Resolution | arbitration, mediation, dispute |
| Payment Terms | payment, net 30, late fee |
| IP | intellectual property, copyright, license |
| Data Protection | GDPR, CCPA, personal data, privacy |
| And ~10 more... | |

### 3. Risk Scoring (`src/analysis/risk_scorer.py`)

Evaluates each clause for risk using clause-specific heuristics.

**Scoring approach:**
- Start at medium (0.5) per clause
- Apply risk weights (+/-) for each detected risk indicator
- 4 risk levels: LOW (<0.25), MEDIUM (<0.50), HIGH (<0.75), CRITICAL (>=0.75)
- Overall risk: weighted average with penalties for multiple high-risk clauses

**Example risk factors:**
- Indemnification: sole discretion (+0.3), mutual (-0.2)
- Limitation of Liability: complete exclusion (+0.3), specific cap (-0.1)
- Confidentiality: perpetual (+0.2), mutual (-0.15)
- Termination: for cause only (+0.15), for convenience (-0.1)

### 4. Redline Generator (`src/analysis/redline_generator.py`)

Generates safer alternative language for high-risk clauses.

**Approach:**
- Template-based suggestions per clause type
- Each template has: trigger pattern, suggestion text, replacement language
- Priority adjusted based on risk score
- Only one redline per clause type (avoids duplication)

### 5. API Layer (`src/api/`)

FastAPI-based REST API for frontend consumption.

**Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | Health check |
| GET | /api/v1/models | Model info and supported clauses |
| GET | /api/v1/clauses | List all supported clause types |
| POST | /api/v1/analyze/file | Upload and analyze a contract |
| POST | /api/v1/analyze/text | Analyze text directly |

## Data Flow

```
1. User uploads PDF/DOCX → POST /api/v1/analyze/file
2. Parser extracts text & section structure → Contract object
3. ClauseDetector scans text & sections → List[Clause]
4. RiskScorer evaluates each clause → List[RiskScore] + overall risk
5. RedlineGenerator creates suggestions → List[RedlineSuggestion]
6. AnalysisResult returned as JSON response
```

## Performance Targets

- **Time-to-review**: < 1 hour per standard contract (currently pattern-based, instant mode already < 30s)
- **Clause detection accuracy**: Target >85% precision/recall for top 15 clause types
- **API response time**: < 5s for typical 20-page contract

## Future Enhancements

1. **LLM-powered analysis** — Use GPT-4/Claude for deeper clause understanding (in progress)
2. **Evaluation framework** — Annotated test set with known clauses for precision/recall measurement
3. **Custom clause libraries** — Per-firm clause patterns and risk preferences
4. **Streaming redlines** — WebSocket endpoint for real-time redline generation
5. **OCR fallback** — Tesseract/OCR for scanned PDFs
6. **Batch analysis** — Queue-based analysis for high-volume firms

## Database Schema (Planned)

```
contracts
├── id, filename, file_type, full_text_hash
├── page_count, parsed_at
└── metadata (JSON)

clauses
├── id, contract_id, clause_type (enum)
├── section_ref, text, confidence
└── start_char, end_char

risk_scores
├── id, clause_id, risk_level, score
└── reasoning, flags (JSON)

redlines
├── id, clause_id, original_text
├── suggested_text, priority
└── risk_reason
```