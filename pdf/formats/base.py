"""Abstract base class for Gehaltszettel PDF format strategies."""

from abc import ABC, abstractmethod


class ValueNotFoundError(Exception):
    """Raised when the Betriebsratsumlage value cannot be found in extracted text."""


class PdfFormat(ABC):
    """Strategy interface for a specific Gehaltszettel PDF format.

    Each subclass encapsulates the glob pattern, filename parsing,
    and value extraction logic for one document layout.
    """

    @property
    @abstractmethod
    def glob_pattern_template(self) -> str:
        """Glob pattern used to discover files of this format.

        Must contain a ``{year}`` placeholder, e.g. ``"{year}*Nettoschein*.pdf"``.

        :return: glob pattern template string
        """

    @abstractmethod
    def extract_month_year(self, filename: str) -> tuple[int, int]:
        """Parse year and month from a PDF *basename*.

        :param filename: basename of the PDF file (no directory component)
        :return: (year, month) as integers
        :raises ValueError: if the filename does not match the expected pattern
        """

    @abstractmethod
    def extract_value(self, text: str) -> float:
        """Extract the Betriebsratsumlage value from the full extracted PDF text.

        :param text: full plain-text content of the PDF
        :return: Betriebsratsumlage value as float
        :raises ValueNotFoundError: if the value cannot be located in text
        """
