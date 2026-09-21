"""Upload local data files to S3, keeping the same folder structure."""

import os
from pathlib import Path

import boto3
import yaml
import dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_settings():
    """Read .env and config.yaml and return the values needed to run."""
    env = dotenv.dotenv_values(PROJECT_ROOT / ".env")
    for key, value in env.items():
        if value:
            os.environ[key] = value.strip()

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

    s3_client = boto3.client("s3", region_name=aws_region)
    for local_file in files:
        relative_path = local_file.relative_to(data_root).as_posix()
        s3_key = f"{s3_prefix}/{relative_path}" if s3_prefix else relative_path
        print(f"Uploading {local_file} to s3://{s3_bucket}/{s3_key}")
        s3_client.upload_file(str(local_file), s3_bucket, s3_key)

    print(f"Uploaded {len(files)} file(s) to s3://{s3_bucket}/{s3_prefix}/")
