"""Abstract parser interface for contract documents."""

from abc import ABC, abstractmethod
from typing import Optional
from src.models import Contract


class BaseParser(ABC):
    """Base class for contract document parsers."""

    @abstractmethod
    def parse(self, file_path: str) -> Contract:
        """
        Parse a contract document and return a structured Contract model.

        Args:
            file_path: Path to the contract file.

        Returns:
            Contract model with extracted text and sections.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file format is unsupported or corrupted.
        """
        pass

    @abstractmethod
    def parse_bytes(self, content: bytes, filename: str) -> Contract:
        """
        Parse contract bytes directly.

        Args:
            content: Raw file bytes.
            filename: Original filename (used to determine format).

        Returns:
            Contract model with extracted text and sections.
        """
        pass