"""Run the full pipeline end to end: local files -> S3 -> Databricks bronze."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from data_ingestion import load_s3_to_bronze, load_to_s3

print("Step 1/2: uploading local data files to S3...")
load_to_s3()

print("\nStep 2/2: loading S3 data into Databricks bronze tables...")
load_s3_to_bronze()

print("\nPipeline complete.")
