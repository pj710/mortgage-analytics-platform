"""Column definitions for the raw Freddie Mac files, shared by ingestion and bronze load."""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def sanitize_column_name(raw_name):
    """Turn a raw pipe-delimited header field into a valid Databricks column name."""
    name = re.sub(r"[^A-Za-z0-9]+", "_", raw_name.strip().lower())
    return name.strip("_")


def read_header_columns(header_file):
    """Read a pipe-delimited header file and return sanitized column names, in order."""
    raw_header = (PROJECT_ROOT / "data" / "headers" / header_file).read_text(encoding="utf-8").strip()
    return [sanitize_column_name(field) for field in raw_header.split("|")]
