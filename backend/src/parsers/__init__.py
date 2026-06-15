"""Contract parsers - extract text and structure from legal documents."""

import os
from typing import Optional
from src.models import Contract
from src.parsers.pdf_parser import PDFParser
from src.parsers.docx_parser import DOCXParser


def get_parser(file_path: str):
    """Return the appropriate parser based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return PDFParser()
    elif ext in ('.docx', '.doc'):
        return DOCXParser()
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def parse_contract(file_path: str) -> Contract:
    """
    Parse a contract from a file path. Auto-detects format from extension.

    Args:
        file_path: Path to the contract file (.pdf, .docx, .doc)

    Returns:
        Structured Contract model.

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If format is unsupported.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    parser = get_parser(file_path)
    return parser.parse(file_path)


def parse_contract_bytes(content: bytes, filename: str) -> Contract:
    """
    Parse a contract from bytes. Auto-detects format from filename.

    Args:
        content: Raw file content.
        filename: Original filename (used to detect format).

    Returns:
        Structured Contract model.
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == '.pdf':
        parser = PDFParser()
    elif ext in ('.docx', '.doc'):
        parser = DOCXParser()
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return parser.parse_bytes(content, filename)