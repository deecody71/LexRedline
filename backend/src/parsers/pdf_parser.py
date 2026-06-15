"""PDF contract parser using PyMuPDF (fitz)."""
import re
import fitz  # PyMuPDF
from typing import List, Optional
from src.models import Contract, Section
from src.parsers.base import BaseParser


class PDFParser(BaseParser):
    """Parse PDF contracts into structured Contract models."""

    HEADING_PATTERN = re.compile(
        r'^(?:'
        r'(?:\d{1,3}(?:\.\d{1,3}){0,3}\.?\s+.*)'  # 1. / 1.1. / 1.2.3.
        r'|'
        r'(?:[A-Z][A-Z\s\-]{3,})'  # ALL CAPS HEADINGS
        r'|'
        r'(?:Section\s+\d+\.?\s*[-–—]?\s*.*)'  # Section 1 - Title
        r')$',
        re.MULTILINE
    )

    def parse(self, file_path: str) -> Contract:
        """Parse a PDF file and extract structured content."""
        doc = fitz.open(file_path)
        return self._extract(doc, file_path)

    def parse_bytes(self, content: bytes, filename: str) -> Contract:
        """Parse PDF from bytes."""
        doc = fitz.open(stream=content, filetype="pdf")
        return self._extract(doc, filename)

    def _extract(self, doc, filename: str) -> Contract:
        """Extract structured content from a fitz Document."""
        full_text_parts = []
        sections: List[Section] = []
        metadata = {}

        # Extract document metadata
        if doc.metadata:
            metadata = {k: v for k, v in doc.metadata.items() if v}

        page_count = len(doc)

        current_section = None
        current_level = 0
        buffer_text = []
        stack = []

        for page_num, page in enumerate(doc):
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b[1], b[0]))  # sort by y then x

            for block in blocks:
                block_text = block[4].strip()
                if not block_text:
                    continue

                # Check if this looks like a heading
                is_heading, level = self._detect_heading(block_text, block)

                if is_heading and level <= 2:
                    # Flush buffer into previous section
                    if buffer_text and stack:
                        stack[-1].content += "\n".join(buffer_text)
                    buffer_text = []

                    new_section = Section(
                        heading=block_text,
                        level=level,
                        content="",
                        start_page=page_num + 1
                    )

                    if not stack:
                        sections.append(new_section)
                        stack = [new_section]
                    else:
                        # Add as subsection if level is deeper
                        if level > stack[-1].level:
                            stack[-1].subsections.append(new_section)
                            stack.append(new_section)
                        else:
                            # Go up the stack
                            while stack and level <= stack[-1].level:
                                stack.pop()
                            if stack:
                                stack[-1].subsections.append(new_section)
                            else:
                                sections.append(new_section)
                            stack.append(new_section)

                    current_section = new_section
                else:
                    buffer_text.append(block_text)

                full_text_parts.append(block_text)

        # Flush remaining buffer
        if buffer_text and stack:
            stack[-1].content += "\n".join(buffer_text)

        doc.close()

        contract = Contract(
            filename=filename,
            file_type="pdf",
            full_text="\n".join(full_text_parts),
            sections=sections,
            page_count=page_count,
            metadata=metadata
        )

        return contract

    def _detect_heading(self, text: str, block: dict) -> tuple[bool, int]:
        """
        Detect if a block is a heading and return its level.
        Returns (is_heading, level).
        """
        if len(text) > 200 or len(text) < 2:
            return False, 0

        # Check for numbered sections (e.g., "1. Definitions", "1.1 Scope")
        if re.match(r'^\d+(?:\.\d+)*\.?\s+\w', text):
            num_parts = text.split()[0].rstrip('.')
            dot_count = num_parts.count('.')
            return True, max(1, dot_count + 1)

        # Check for ALL CAPS (short enough to be a heading)
        if text.isupper() and len(text) < 100 and len(text.split()) <= 12:
            return True, 1

        # Check for "Section X" pattern
        if re.match(r'^Section\s+\d+', text, re.IGNORECASE):
            return True, 1

        # Check for typical heading keywords
        heading_keywords = [
            'agreement', 'definitions', 'scope', 'terms', 'payment',
            'delivery', 'warranty', 'indemnification', 'confidentiality',
            'termination', 'governing', 'limitation', 'assignment',
            'dispute', 'force majeure', 'insurance', 'representations',
            'covenants', 'general provisions', 'miscellaneous'
        ]

        text_lower = text.lower().rstrip(':')
        for keyword in heading_keywords:
            if text_lower == keyword or text_lower.startswith(keyword):
                return True, 1

        return False, 0