"""Copy raw Freddie Mac files from S3 into the Databricks bronze layer."""

import os
import re
from pathlib import Path

import boto3
import dotenv
import yaml
from databricks import sql
from databricks.sdk.core import Config

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Each entry maps a header file (defines bronze column order) to its bronze
# table and the config.yaml paths key holding the matching S3 sub-folder.
BRONZE_DATASETS = [
    {
        "table": "originations_raw",
        "header_file": "origination_data_file_header.txt",
        "path_key": "originations_data",
    },
    {
        "table": "performance_raw",
        "header_file": "performance_data_file_header.txt",
        "path_key": "performance_data",
    },
]


def get_settings():
    """Read .env and config.yaml and return the values needed to run."""
    env = dotenv.dotenv_values(PROJECT_ROOT / ".env")
    for key, value in env.items():
        if value:
            os.environ[key] = value.strip()

    with open(PROJECT_ROOT / "config" / "config.yaml", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    s3_bucket = (os.getenv("S3_BUCKET") or config["aws"].get("s3_bucket") or "").strip()
    s3_prefix = (os.getenv("S3_PREFIX") or config["aws"].get("s3_prefix") or "").strip("/")
    aws_key_id = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    aws_region = (os.getenv("AWS_DEFAULT_REGION") or config["aws"].get("region") or "").strip()

    # Unified auth: Config resolves credentials itself (PAT, OAuth M2M, Azure
    # CLI/MSI, config profile, etc.), so host/token are not required here.
    db_config = config.get("databricks", {})
    databricks_settings = {
        "host": (os.getenv("DATABRICKS_HOST") or os.getenv("DATABRICKS_SERVER_HOSTNAME") or "").strip(),
        "http_path": os.getenv("DATABRICKS_HTTP_PATH", "").strip(),
        "profile": os.getenv("DATABRICKS_CONFIG_PROFILE", "").strip(),
        "catalog": (os.getenv("DATABRICKS_CATALOG") or db_config.get("catalog") or "").strip(),
    }
    bronze_schema = (os.getenv("DATABRICKS_BRONZE_SCHEMA") or db_config.get("bronze_schema") or "bronze").strip()

    required = {
        "S3_BUCKET": s3_bucket,
        "AWS_ACCESS_KEY_ID": aws_key_id,
        "AWS_SECRET_ACCESS_KEY": aws_secret_key,
        "DATABRICKS_HTTP_PATH": databricks_settings["http_path"],
        "DATABRICKS_CATALOG": databricks_settings["catalog"],
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(
            f"Missing required settings: {', '.join(missing)}. "
            "Set them in .env or config/config.yaml."
        )

    return {
        "s3_bucket": s3_bucket,
        "s3_prefix": s3_prefix,
        "aws_key_id": aws_key_id,
        "aws_secret_key": aws_secret_key,
        "aws_region": aws_region,
        "bronze_schema": bronze_schema,
        "paths": config["paths"],
        "databricks": databricks_settings,
    }


def sanitize_column_name(raw_name):
    """Turn a raw pipe-delimited header field into a valid Databricks column name."""
    name = re.sub(r"[^A-Za-z0-9]+", "_", raw_name.strip().lower())
    return name.strip("_")


def read_header_columns(header_file):
    """Read a pipe-delimited header file and return sanitized column names, in order."""
    raw_header = (PROJECT_ROOT / "data" / "headers" / header_file).read_text(encoding="utf-8").strip()
    return [sanitize_column_name(field) for field in raw_header.split("|")]


def dataset_s3_subpath(paths, path_key):
    """Return a dataset's folder path relative to the data root (e.g. freddie_raw/originations)."""
    return Path(paths[path_key]).relative_to(Path(paths["data_root"])).as_posix()


def get_temporary_aws_credentials(aws_key_id, aws_secret_key, aws_region):
    """Exchange long-lived AWS keys for an STS session; Databricks COPY INTO requires a session token."""
    sts_client = boto3.client(
        "sts",
        aws_access_key_id=aws_key_id,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region or None,
    )
    credentials = sts_client.get_session_token(DurationSeconds=3600)["Credentials"]
    return credentials["AccessKeyId"], credentials["SecretAccessKey"], credentials["SessionToken"]


def build_connection(databricks_settings):
    """Connect using Databricks unified authentication (PAT, OAuth M2M, Azure, or CLI profile)."""
    config = Config(
        host=databricks_settings["host"] or None,
        profile=databricks_settings["profile"] or None,
    )
    return sql.connect(
        server_hostname=config.host,
        http_path=databricks_settings["http_path"],
        credentials_provider=lambda: config.authenticate,
        catalog=databricks_settings["catalog"],
    )


def ensure_bronze_schema(cursor, catalog, bronze_schema):
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{bronze_schema}")


def ensure_bronze_table(cursor, catalog, bronze_schema, table, columns):
    """Create the bronze table if missing. All source fields land as STRING; typing happens downstream."""
    column_defs = ",\n            ".join(f"{col} STRING" for col in columns)
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {catalog}.{bronze_schema}.{table} (
            {column_defs},
            source_file STRING,
            loaded_at TIMESTAMP
        )
        """
    )


def copy_into_bronze(cursor, catalog, bronze_schema, table, columns, bucket, prefix, stage_subpath, aws_credentials):
    """COPY INTO the bronze table from S3, tagging each row with its source file.

    Uses inline temporary AWS credentials for portfolio simplicity; production
    Databricks setups should use a Unity Catalog storage credential/external
    location instead.
    """
    aws_key_id, aws_secret_key, aws_session_token = aws_credentials
    source_path = f"s3://{bucket}/{prefix}/{stage_subpath}/" if prefix else f"s3://{bucket}/{stage_subpath}/"
    select_columns = ", ".join(f"_c{i}::string AS {col}" for i, col in enumerate(columns))
    cursor.execute(
        f"""
        COPY INTO {catalog}.{bronze_schema}.{table}
        FROM (
            SELECT {select_columns}, _metadata.file_name AS source_file, current_timestamp() AS loaded_at
            FROM '{source_path}' WITH (CREDENTIAL (
                AWS_ACCESS_KEY = '{aws_key_id}',
                AWS_SECRET_KEY = '{aws_secret_key}',
                AWS_SESSION_TOKEN = '{aws_session_token}'
            ))
        )
        FILEFORMAT = CSV
        FORMAT_OPTIONS ('delimiter' = '|', 'header' = 'false')
        COPY_OPTIONS ('mergeSchema' = 'true')
        """
    )
    return cursor.fetchall()


def load_s3_to_bronze(settings=None):
    """Copy every configured Freddie Mac dataset from S3 into its Databricks bronze table."""
    if settings is None:
        settings = get_settings()

    catalog = settings["databricks"]["catalog"]
    bronze_schema = settings["bronze_schema"]

    aws_credentials = get_temporary_aws_credentials(
        settings["aws_key_id"], settings["aws_secret_key"], settings["aws_region"]
    )

    connection = build_connection(settings["databricks"])
    try:
        cursor = connection.cursor()
        ensure_bronze_schema(cursor, catalog, bronze_schema)

        for dataset in BRONZE_DATASETS:
            columns = read_header_columns(dataset["header_file"])
            ensure_bronze_table(cursor, catalog, bronze_schema, dataset["table"], columns)

            stage_subpath = dataset_s3_subpath(settings["paths"], dataset["path_key"])
            target = f"{catalog}.{bronze_schema}.{dataset['table']}"
            print(f"Copying s3://{settings['s3_bucket']}/{settings['s3_prefix']}/{stage_subpath}/ -> {target}")

            for row in copy_into_bronze(
                cursor,
                catalog,
                bronze_schema,
                dataset["table"],
                columns,
                settings["s3_bucket"],
                settings["s3_prefix"],
                stage_subpath,
                aws_credentials,
            ):
                print(row)
    finally:
        connection.close()
