"""Load raw Freddie Mac files from S3 into the Databricks bronze layer."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from data_ingestion import load_s3_to_bronze

load_s3_to_bronze()
