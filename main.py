"""
Extract data from "Gehaltszettel" and write to csv format
"""

import os
import sys
import argparse
import logging
from typing import Sequence, Optional
from dotenv import load_dotenv, find_dotenv
from pdf import get_pdfs
from betriebsratsumlage import Betriebsratsumlage, ValueNotFoundError


def load_password() -> Optional[str]:
    """
    Load password from .env file
    .env example:
    password=1234
    :return: password on success, else None
    """
    return os.getenv("password") if load_dotenv(find_dotenv()) else None


def write_csv(path: str, data: dict[int | str, float], delimiter: str = ";") -> None:
    """
    Write dictionary to csv file
    :param path: csv output file path
    :param data: data to be written to csv file
    :param delimiter: csv delimiter (default=;)
    """

    def float_to_str(v: float) -> str:
        s: str = f"{v:.2f}"
        return s.replace(".", ",") if delimiter == ";" else s

    with open(path, "w", encoding="utf-8") as csv:
        for month, value in data.items():
            csv.write(f"{month}{delimiter}{float_to_str(value)}\n")
        csv.write(f"Sum:{delimiter}{float_to_str(sum(data.values()))}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    main function
    :param argv: argument values (default=None)
    :return: 0 on success, else error code >0
    """
    csv_file = "Betriebsratsumlage.csv"
    bru = Betriebsratsumlage()
    error = False

    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("year")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    pwd = load_password()
    if pwd is None:
        logging.error("Could not load password from '.env' file")
        return 1

    pdfs = get_pdfs(args.path, args.year)
    if not pdfs:
        logging.error("No pdf files found with the provided parameters")
        return 1

    # extract Betriebsratsumlage from each pdf
    for pdf_file in pdfs:
        try:
            pdf_file.read_text(pwd)
            v = bru.get_value_from_text(pdf_file.month, pdf_file.text)
            logging.info(f"{pdf_file.month:>2} {v:.2f}")
        except RuntimeError as e:
            logging.error(e)
            error = True
            continue
        except ValueNotFoundError as e:
            logging.error(f"{e} in '{pdf_file.path}'")
            error = True
            continue

    # check if any month is missing
    if diff := set(range(1, 13)) - set(bru.months):
        logging.error(f"Missing months: {', '.join(str(d) for d in diff)}")
        error = True

    logging.info(f"Sum: {bru.sum:>.2f}")

    write_csv(csv_file, bru.months)
    logging.info(f"csv output: '{csv_file}'")

    if error:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
