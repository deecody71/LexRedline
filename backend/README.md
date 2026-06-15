# LexRedline Contract Engine

AI-powered contract review engine that scans contracts, flags risky clauses, and suggests redlines.

## Architecture Overview

```
src/
├── models/          # Pydantic data models
│   ├── __init__.py
│   ├── contract.py   # Contract, Section, Clause models
│   └── analysis.py   # RiskScore, RedlineSuggestion, AnalysisResult
├── parsers/         # Document parsers
│   ├── __init__.py
│   ├── base.py       # Abstract parser interface
│   ├── pdf_parser.py # PDF text extraction (PyMuPDF)
│   └── docx_parser.py # DOCX parsing (python-docx)
├── analysis/        # Analysis engine
│   ├── __init__.py
│   ├── clause_detector.py   # Clause classification
│   ├── risk_scorer.py       # Risk scoring per clause
│   └── redline_generator.py # Redline suggestion engine
├── api/             # FastAPI REST endpoints
│   ├── __init__.py
│   ├── routes.py     # API routes
│   └── schemas.py    # Request/response schemas
├── config.py        # Configuration
├── main.py          # FastAPI app entry point
└── __init__.py
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Start the API server

```bash
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 3000
```

### Parse a contract

```python
from src.parsers.pdf_parser import PDFParser
from src.parsers.docx_parser import DOCXParser

# Parse a PDF
pdf_parser = PDFParser()
contract = pdf_parser.parse("path/to/contract.pdf")

# Parse a DOCX
docx_parser = DOCXParser()
contract = docx_parser.parse("path/to/contract.docx")
```

### Run analysis

```python
from src.analysis.clause_detector import ClauseDetector
from src.analysis.risk_scorer import RiskScorer
from src.analysis.redline_generator import RedlineGenerator

detector = ClauseDetector()
scorer = RiskScorer()
generator = RedlineGenerator()

clauses = detector.detect(contract)
risk_scores = scorer.score(clauses)
redlines = generator.suggest(clauses)
```

## Development

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src -v
```
