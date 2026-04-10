"""Format strategy for ZeitNet Gehaltszettel PDFs.

Filename pattern: YYYYMM_*Nettoschein*.pdf  (e.g. 202412_Nettoschein_Firma_3_PSNR_51569.pdf)
"""

import re

from .base import PdfFormat, ValueNotFoundError


class ZeitNetFormat(PdfFormat):
    """Format strategy for ZeitNet Gehaltszettel PDFs."""

    @property
    def glob_pattern_template(self) -> str:
        """Glob pattern used to discover files of this format.

        Must contain a ``{year}`` placeholder, e.g. ``"{year}*Nettoschein*.pdf"``.

        :return: glob pattern template string
        """
        return "{year}*Nettoschein*.pdf"

    def extract_month_year(self, filename: str) -> tuple[int, int]:
        """Parse year and month from a PDF *basename*.

        :param filename: basename of the PDF file (no directory component)
        :return: (year, month) as integers
        :raises ValueError: if the filename does not match the expected pattern
        """
        m = re.search(r"^(\d{4})(\d{2})", filename)
        if not m:
            raise ValueError(f"Cannot extract year/month from filename: '{filename}'")
        return int(m.group(1)), int(m.group(2))

    def extract_value(self, text: str) -> float:
        """Extract the Betriebsratsumlage value from the full extracted PDF text.

        :param text: full plain-text content of the PDF
        :return: Betriebsratsumlage value as float
        :raises ValueNotFoundError: if the value cannot be located in text
        """
        matches = re.findall(r"841\s+Betriebsratsuml[a-zA-Z.]*[a-zA-Z. ]+ (\d+,\d+)-", text)
        if not matches:
            raise ValueNotFoundError("Betriebsratsumlage value not found (ZeitNet)")
        return sum(float(v.replace(",", ".")) for v in matches)
