"""Upload local data files to S3 (raw pipe-delimited files as parquet), keeping the same folder structure."""

import os
import tempfile
from pathlib import Path

import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import yaml
import dotenv

from .schema import PROJECT_ROOT, read_header_columns

CHUNK_ROWS = 500_000

# Raw pipe-delimited datasets are stored in S3 as parquet. Maps each dataset's
# config.yaml paths key to the header file defining its column names.
RAW_DATASETS = {
    "originations_data": "origination_data_file_header.txt",
    "performance_data": "performance_data_file_header.txt",
}


def get_settings():
    """Read .env and config.yaml and return the values needed to run."""
    env = dotenv.dotenv_values(PROJECT_ROOT / ".env")
    for key, value in env.items():
        if value:
            os.environ[key] = value.strip()

    # Without this, botocore computes a client-side checksum on every upload; without the
    # crc32c C extension installed, that falls back to a pure-Python hash that is orders of
    # magnitude slower, making uploads of our larger (multi-10MB+) sample files appear to hang.
    os.environ.setdefault("AWS_REQUEST_CHECKSUM_CALCULATION", "when_required")

    # An empty AWS_PROFILE makes boto3 fail, so drop it if it has no value.
    if not os.getenv("AWS_PROFILE", "").strip():
        os.environ.pop("AWS_PROFILE", None)

    with open(PROJECT_ROOT / "config" / "config.yaml", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    data_root = PROJECT_ROOT / config["paths"]["data_root"]
    s3_bucket = (os.getenv("S3_BUCKET") or config["aws"].get("s3_bucket") or "").strip()
    s3_prefix = (os.getenv("S3_PREFIX") or config["aws"].get("s3_prefix") or "").strip("/")
    aws_region = os.getenv("AWS_DEFAULT_REGION") or config["aws"]["region"]

    if not s3_bucket:
        raise ValueError("S3_BUCKET is required. Set it in .env or config/config.yaml.")
    if not data_root.is_dir():
        raise FileNotFoundError(f"Data directory does not exist: {data_root}")

    return data_root, s3_bucket, s3_prefix, aws_region


def raw_dataset_headers():
    """Map each raw dataset directory to the header file naming its columns."""
    with open(PROJECT_ROOT / "config" / "config.yaml", encoding="utf-8") as config_file:
        paths = yaml.safe_load(config_file)["paths"]
    return {(PROJECT_ROOT / paths[key]).resolve(): header for key, header in RAW_DATASETS.items()}


def convert_to_parquet(source_file, header_file, target_file):
    """Stream a pipe-delimited file into parquet in chunks; every column is kept as a string."""
    columns = read_header_columns(header_file)
    writer = None
    try:
        reader = pd.read_csv(
            source_file,
            sep="|",
            header=None,
            names=columns,
            dtype=str,
            keep_default_na=False,
            na_values=[""],
            chunksize=CHUNK_ROWS,
        )
        for chunk in reader:
            table = pa.Table.from_pandas(chunk, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(target_file, table.schema, compression="snappy")
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()
    if writer is None:
        raise ValueError(f"No rows found in {source_file}")


def find_files(data_root):
    """Return every non-hidden file under data_root."""
    return sorted(
        path
        for path in data_root.rglob("*")
        if path.is_file() and not path.name.startswith(".")
    )


def load_to_s3(settings=None):
    """Upload every local data file to S3, keeping the same folder layout."""
    if settings is None:
        data_root, s3_bucket, s3_prefix, aws_region = get_settings()
    else:
        data_root, s3_bucket, s3_prefix, aws_region = settings
    files = find_files(data_root)
    if not files:
        raise FileNotFoundError(f"No files found under data directory: {data_root}")

    dataset_headers = raw_dataset_headers()
    s3_client = boto3.client("s3", region_name=aws_region)
    with tempfile.TemporaryDirectory() as temp_dir:
        for local_file in files:
            relative_path = local_file.relative_to(data_root)
            upload_file = local_file
            header_file = dataset_headers.get(local_file.parent.resolve())
            if header_file and local_file.suffix.lower() == ".txt":
                relative_path = relative_path.with_suffix(".parquet")
                upload_file = Path(temp_dir) / relative_path.name
                print(f"Converting {local_file} to parquet")
                convert_to_parquet(local_file, header_file, upload_file)

            relative_key = relative_path.as_posix()
            s3_key = f"{s3_prefix}/{relative_key}" if s3_prefix else relative_key
            print(f"Uploading {upload_file} to s3://{s3_bucket}/{s3_key}")
            s3_client.upload_file(str(upload_file), s3_bucket, s3_key)
            if upload_file != local_file:
                upload_file.unlink()

    print(f"Uploaded {len(files)} file(s) to s3://{s3_bucket}/{s3_prefix}/")
