from .base import PdfFormat, ValueNotFoundError
from .sap import SapFormat
from .zeit_net import ZeitNetFormat

FORMATS: list[PdfFormat] = [
    ZeitNetFormat(),
    SapFormat(),
]
