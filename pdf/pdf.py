"""Read Gehaltszettel pdf files."""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from pdf.formats import FORMATS
from pdf.formats.base import PdfFormat


class PdfError(Exception):
    """Base class for PDF-related errors."""

@dataclass
class Pdf:
    """Gehaltszettel pdf."""

    path: Path = field(compare=False)
    fmt: PdfFormat = field(compare=False)
    year: int = field(init=False, compare=False)
    month: int = field(init=False, compare=False)
    text: str = field(init=False, repr=False, compare=False, default="")

    def __post_init__(self):
        """Post construction initialization."""
        self.year, self.month = self.fmt.extract_month_year(self.path.name)

    def read_text(self, get_password: Callable[[], str | None] | None = None) -> None:
        """Read text of pdf file.

        :param get_password: callable invoked only when the file is encrypted;
                             should return the password string or None
        """
        try:
            reader = PdfReader(self.path)
        except PdfReadError as e:
            raise PdfError(f"Error reading '{self.path}': {e}") from e

        if reader.is_encrypted:
            pwd = get_password() if get_password is not None else None
            if pwd is None:
                raise PdfError(f"'{self.path}' is encrypted but no password was provided")
            try:
                if not reader.decrypt(pwd):
                    raise PdfError(f"Invalid password for '{self.path}'")
            except PdfReadError as e:
                raise PdfError(f"Error decrypting '{self.path}': {e}") from e

        for page in reader.pages:
            self.text += page.extract_text() + "\n"


def get_pdfs(path: Path, year: str) -> list[Pdf]:
    """Get all Gehaltszettel pdf files in a given path for all known formats of a given year.

    :param path: directory to be searched
    :param year: year to be collected
    :return: sorted list of Pdfs
    """
    pdfs: list[Pdf] = []

    for fmt in FORMATS:
        pattern = fmt.glob_pattern_template.format(year=year)
        pdfs.extend(Pdf(path=p, fmt=fmt) for p in path.glob(pattern))
    return sorted(pdfs, key=lambda p: (p.year, p.month))
