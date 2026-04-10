# Gehaltszettel Reader

A command-line tool that extracts payroll data from German "Gehaltszettel" PDF files and outputs the results as CSV.

## Features

- Parses multiple PDF payslip formats (SAP, Zeit.Net)
- Extracts Betriebsratsumlage per month and computes the annual sum
- Supports password-protected PDFs via `.env` file or interactive prompt
- Outputs a semicolon-delimited CSV file

## Requirements

- Python >= 3.11
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Setup

```bash
git clone <repository-url>
cd Gehaltszettel_Reader
uv sync
```

For password-protected PDFs, create a `.env` file in the project root:

```ini
PASSWORD=your_pdf_password
```

If no `.env` file is present and the PDF is encrypted, the password will be requested interactively at runtime.

## Usage

```
usage: main.py [-h] [--version] path year

positional arguments:
  path        Directory to search for Gehaltszettel PDF files
  year        Year to collect (e.g. 2024)

options:
  -h, --help  Show this help message and exit
  --version   Show program version and exit
```

### Examples

```bash
# Extract Betriebsratsumlage for 2024
python main.py /home/username/Gehaltsabrechnung 2024

# Windows
python main.py "C:\Users\username\Gehaltsabrechnung" 2024
```

The output is written to `Betriebsratsumlage.csv` in the current working directory.

## Output Format

The CSV file uses a semicolon delimiter and German decimal notation (comma as decimal separator):

```
1;123,45
2;130,00
...
Sum:;1560,00
```

## License

This project is licensed under the [MIT License](LICENSE).