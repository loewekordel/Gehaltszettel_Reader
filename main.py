"""Extract data from "Gehaltszettel" and write to csv format."""

import argparse
import getpass
import logging
import os
import tomllib
from collections.abc import Callable, Sequence
from importlib.metadata import version
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from betriebsratsumlage import Betriebsratsumlage
from pdf import PdfError, get_pdfs
from pdf.formats.base import ValueNotFoundError

logger = logging.getLogger(__name__)


def make_password_provider() -> Callable[[], str | None]:
    """Returns a callable that resolves the PDF password on first need.

    Checks .env first; falls back to an interactive prompt.
    The resolved password is cached so the user is only asked once.
    :return: callable that returns the PDF password
    """
    load_dotenv(find_dotenv())
    cache: list[str | None] = []  # single-element list used as a mutable cell

    def get_password() -> str | None:
        """Get the PDF password, prompting the user if necessary.

        :return: PDF password or None if not provided
        """
        if not cache:
            pwd = os.getenv("PASSWORD") or getpass.getpass("PDF password (press Enter to skip): ") or None
            cache.append(pwd)
        return cache[0]

    return get_password


def get_version() -> str:
    """Return the package version.

    Tries importlib.metadata first (installed package), then falls back to
    reading pyproject.toml directly.

    :return: version string, or 'unknown' if it cannot be determined
    """
    try:
        return version("gehaltszettel-reader")
    except Exception: # noqa: BLE001 # blindly catch all exceptions to avoid any issues with version retrieval
        try:
            _pyproject = Path(__file__).parent / "pyproject.toml"
            return tomllib.loads(_pyproject.read_text(encoding="utf-8"))["project"]["version"]
        except Exception: # noqa: BLE001 # blindly catch all exceptions to avoid any issues with version retrieval
            return "unknown"


def write_csv(path: Path, data: dict[int | str, float], delimiter: str = ";") -> None:
    """Write dictionary to csv file.

    :param path: csv output file path
    :param data: data to be written to csv file
    :param delimiter: csv delimiter (default=;)
    """

    def float_to_str(v: float) -> str:
        """Convert float to string with 2 decimal places, using comma as decimal separator.

        :param v: float value to convert
        :return: string representation of the float with 2 decimal places
        """
        s: str = f"{v:.2f}"
        return s.replace(".", ",") if delimiter == ";" else s

    with path.open("w", encoding="utf-8") as csv:
        for month, value in data.items():
            csv.write(f"{month}{delimiter}{float_to_str(value)}\n")
        csv.write(f"Sum:{delimiter}{float_to_str(sum(data.values()))}")


def main(argv: Sequence[str] | None = None) -> int:
    """Main function.

    :param argv: argument values (default=None)
    :return: 0 on success, else error code >0
    """
    csv_file = Path("Betriebsratsumlage.csv")
    bru = Betriebsratsumlage()
    error = False

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="directory to be searched for Gehaltszettel pdf files")
    parser.add_argument("year", type=str, help="year to be collected (e.g. 2024)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {get_version()}")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    get_password = make_password_provider()

    pdfs = get_pdfs(args.path, args.year)
    if not pdfs:
        logger.error("No pdf files found with the provided parameters")
        return 1

    # extract Betriebsratsumlage from each pdf
    for pdf_file in pdfs:
        try:
            pdf_file.read_text(get_password)
            value = pdf_file.fmt.extract_value(pdf_file.text)
            bru.add(pdf_file.month, value)
            logger.info(f"Month: {pdf_file.month:>2} Value: {value:.2f} (extracted from '{pdf_file.path}')")
        except PdfError as e:
            logger.error(e)
            error = True
            continue
        except ValueNotFoundError as e:
            logger.error(f"{e} in '{pdf_file.path}'")
            error = True
            continue

    # check if any month is missing
    if diff := set(range(1, 13)) - set(bru.months):
        logger.error(f"Missing months: {', '.join(str(d) for d in diff)}")
        error = True

    logger.info(f"Sum: {bru.sum:>.2f}")

    write_csv(csv_file, bru.months)
    logger.info(f"csv output: '{csv_file}'")

    if error:
        logger.error("Errors occurred during processing")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
