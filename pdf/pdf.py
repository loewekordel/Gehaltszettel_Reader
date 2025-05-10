"""
Read Gehaltszettel pdf files
"""

import os
import re
import glob
from dataclasses import dataclass, field
from PyPDF2 import PdfReader, PasswordType
from PyPDF2.errors import PdfReadError


@dataclass
class Pdf:
    """
    Gehaltszettel pdf
    """
    path: str = field(compare=False)
    year: int = field(init=False, compare=False)
    month: int = field(init=False, compare=False)
    text: str = field(init=False, repr=False, compare=False, default="")

    def __post_init__(self):
        self.year, self.month = [
            int(v)
            for v in re.search(r"^(\d{4})(\d{2})", os.path.basename(self.path)).groups()
        ]

    def read_text(self, pwd: str) -> None:
        """
        read text of pdf files
        :param pwd: password of encrypted files
        """
        reader = PdfReader(self.path)

        # if file is encrypted, decrypt it
        if reader.is_encrypted:
            try:
                password_type: PasswordType = reader.decrypt(pwd)
                # check if password is correct
                if password_type == PasswordType.NOT_DECRYPTED:
                    raise RuntimeError(f"Invalid password for '{self.path}'")
            except PdfReadError as e:
                raise RuntimeError(f"Error reading '{self.path}': {e}") from e

        for page in reader.pages:
            self.text += page.extract_text() + "\n"


def get_pdfs(path: str, year: str) -> list[Pdf]:
    """
    get all Gehaltszettel pdf files in a given path of a given year
    :param path: directory to be searched
    :param year: year to be collected
    :return: list of Pdfs
    """
    files = glob.iglob(rf"{year}*Nettoschein*.pdf", root_dir=path)
    return [Pdf(os.path.join(path, f)) for f in files]
