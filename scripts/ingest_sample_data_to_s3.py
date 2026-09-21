"""Run the data-ingestion pipeline."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from data_ingestion import load_to_s3

load_to_s3()