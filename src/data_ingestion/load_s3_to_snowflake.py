"""Copy raw Freddie Mac files from S3 into the Snowflake bronze layer."""

import os
import re
from pathlib import Path

import dotenv
import snowflake.connector
import yaml

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

    sf_config = config.get("snowflake", {})
    snowflake_settings = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT", "").strip(),
        "user": os.getenv("SNOWFLAKE_USER", "").strip(),
        "password": os.getenv("SNOWFLAKE_PASSWORD", "").strip(),
        "warehouse": (os.getenv("SNOWFLAKE_WAREHOUSE") or sf_config.get("warehouse") or "").strip(),
        "database": (os.getenv("SNOWFLAKE_DATABASE") or sf_config.get("database") or "").strip(),
        "role": (os.getenv("SNOWFLAKE_ROLE") or sf_config.get("role") or "").strip(),
    }
    bronze_schema = (os.getenv("SNOWFLAKE_BRONZE_SCHEMA") or sf_config.get("bronze_schema") or "BRONZE").strip()

    required = {
        "S3_BUCKET": s3_bucket,
        "AWS_ACCESS_KEY_ID": aws_key_id,
        "AWS_SECRET_ACCESS_KEY": aws_secret_key,
        "SNOWFLAKE_ACCOUNT": snowflake_settings["account"],
        "SNOWFLAKE_USER": snowflake_settings["user"],
        "SNOWFLAKE_PASSWORD": snowflake_settings["password"],
        "SNOWFLAKE_WAREHOUSE": snowflake_settings["warehouse"],
        "SNOWFLAKE_DATABASE": snowflake_settings["database"],
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
        "bronze_schema": bronze_schema,
        "paths": config["paths"],
        "snowflake": snowflake_settings,
    }


def sanitize_column_name(raw_name):
    """Turn a raw pipe-delimited header field into a valid Snowflake column name."""
    name = re.sub(r"[^A-Za-z0-9]+", "_", raw_name.strip().upper())
    return name.strip("_")


def read_header_columns(header_file):
    """Read a pipe-delimited header file and return sanitized column names, in order."""
    raw_header = (PROJECT_ROOT / "data" / "headers" / header_file).read_text(encoding="utf-8").strip()
    return [sanitize_column_name(field) for field in raw_header.split("|")]


def dataset_s3_subpath(paths, path_key):
    """Return a dataset's folder path relative to the data root (e.g. freddie_raw/originations)."""
    return Path(paths[path_key]).relative_to(Path(paths["data_root"])).as_posix()


def build_connection(snowflake_settings):
    return snowflake.connector.connect(
        account=snowflake_settings["account"],
        user=snowflake_settings["user"],
        password=snowflake_settings["password"],
        warehouse=snowflake_settings["warehouse"],
        database=snowflake_settings["database"],
        role=snowflake_settings["role"] or None,
    )


def ensure_bronze_schema(cursor, database, bronze_schema):
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {database}.{bronze_schema}")


def ensure_stage(cursor, database, bronze_schema, bucket, prefix, aws_key_id, aws_secret_key):
    """Create/replace the external stage pointing at the S3 landing area.

    Snowflake stores stage credentials encrypted and masks them in query
    history, but for production use prefer a storage integration (IAM role
    trust) instead of static keys.
    """
    stage_url = f"s3://{bucket}/{prefix}/" if prefix else f"s3://{bucket}/"
    cursor.execute(
        f"""
        CREATE OR REPLACE STAGE {database}.{bronze_schema}.s3_raw_stage
        URL = '{stage_url}'
        CREDENTIALS = (AWS_KEY_ID = '{aws_key_id}' AWS_SECRET_KEY = '{aws_secret_key}')
        FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = '|' EMPTY_FIELD_AS_NULL = TRUE NULL_IF = (''))
        """
    )


def ensure_bronze_table(cursor, database, bronze_schema, table, columns):
    """Create the bronze table if missing. All source fields land as STRING; typing happens downstream."""
    column_defs = ",\n            ".join(f"{col} STRING" for col in columns)
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {database}.{bronze_schema}.{table} (
            {column_defs},
            source_file STRING,
            file_row_number NUMBER,
            loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
    )


def copy_into_bronze(cursor, database, bronze_schema, table, columns, stage_subpath):
    """COPY INTO the bronze table from the stage, tagging each row with its source file."""
    select_columns = ", ".join(f"${i}" for i in range(1, len(columns) + 1))
    target_columns = ", ".join(columns + ["source_file", "file_row_number"])
    cursor.execute(
        f"""
        COPY INTO {database}.{bronze_schema}.{table} ({target_columns})
        FROM (
            SELECT {select_columns}, METADATA$FILENAME, METADATA$FILE_ROW_NUMBER
            FROM @{database}.{bronze_schema}.s3_raw_stage/{stage_subpath}/
        )
        FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = '|' EMPTY_FIELD_AS_NULL = TRUE NULL_IF = (''))
        PATTERN = '.*\\.txt'
        ON_ERROR = 'CONTINUE'
        """
    )
    return cursor.fetchall()


def load_s3_to_bronze(settings=None):
    """Copy every configured Freddie Mac dataset from S3 into its Snowflake bronze table."""
    if settings is None:
        settings = get_settings()

    database = settings["snowflake"]["database"]
    bronze_schema = settings["bronze_schema"]

    connection = build_connection(settings["snowflake"])
    try:
        cursor = connection.cursor()
        ensure_bronze_schema(cursor, database, bronze_schema)
        ensure_stage(
            cursor,
            database,
            bronze_schema,
            settings["s3_bucket"],
            settings["s3_prefix"],
            settings["aws_key_id"],
            settings["aws_secret_key"],
        )

        for dataset in BRONZE_DATASETS:
            columns = read_header_columns(dataset["header_file"])
            ensure_bronze_table(cursor, database, bronze_schema, dataset["table"], columns)

            stage_subpath = dataset_s3_subpath(settings["paths"], dataset["path_key"])
            target = f"{database}.{bronze_schema}.{dataset['table']}"
            print(f"Copying s3://{settings['s3_bucket']}/{settings['s3_prefix']}/{stage_subpath}/ -> {target}")

            for row in copy_into_bronze(cursor, database, bronze_schema, dataset["table"], columns, stage_subpath):
                print(row)
    finally:
        connection.close()
