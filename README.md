# Mortgage Analytics Platform

A U.S. residential mortgage analytics data platform built on the Freddie Mac
Single-Family Loan-Level Dataset. Raw origination and monthly performance
files are landed in S3, loaded into a Databricks lakehouse bronze layer, and
transformed with dbt into a canonical, documented, and tested core schema for
portfolio, delinquency, vintage, and loss analysis.

See [mortgage-analytics-project-charter.md](mortgage-analytics-project-charter.md)
for full project scope, objectives, and metric definitions.

## Architecture

```
Local sample files (data/freddie_raw/)
        │  scripts/ingest_sample_data_to_s3.py
        ▼
Amazon S3
        │  scripts/load_s3_to_databricks_bronze.py  (COPY INTO)
        ▼
Databricks bronze schema (raw, untyped STRING columns)
        │  dbt (dbt/)
        ▼
Databricks staging schema (typed, renamed views)
        │
        ▼
Databricks core schema (dim_loan, dim_geography, dim_period,
                         fact_loan_performance)
```

## Project structure

```
config/config.yaml         Non-secret settings (AWS bucket/region, Databricks catalog/schema)
data/                       Sample Freddie Mac origination and performance files, plus headers
src/data_ingestion/         Python ingestion library (S3 upload, Databricks bronze load)
scripts/                    Thin CLI entry points that call the ingestion library
dbt/                        dbt project: staging + core models, macros, tests, docs
```

## Prerequisites

- Python 3.9+
- An AWS account/IAM user with access to an S3 bucket
- A Databricks workspace with Unity Catalog and a SQL warehouse

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root (gitignored) with:

```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=...
S3_PREFIX=...

DATABRICKS_SERVER_HOSTNAME=...
DATABRICKS_HTTP_PATH=...
DATABRICKS_TOKEN=...
DATABRICKS_CATALOG=...
```

Non-secret defaults (bucket, region, catalog, schema names) live in
[config/config.yaml](config/config.yaml) and are overridden by the env vars
above when set.

## Running the pipeline

Upload sample data to S3 and load it into the Databricks bronze layer:

```bash
python scripts/run_pipeline.py
```

Or run each stage independently:

```bash
python scripts/ingest_sample_data_to_s3.py
python scripts/load_s3_to_databricks_bronze.py
```

## Running the dbt transformations

`.env` uses `KEY = VALUE` spacing, so export it into the shell first, then run
dbt from the `dbt/` directory:

```bash
eval "$(python3 -c "
import dotenv
for k, v in dotenv.dotenv_values('.env').items():
    if v:
        print(f'export {k}=\"{v.strip()}\"')
")"
cd dbt
DBT_PROFILES_DIR=. dbt run
DBT_PROFILES_DIR=. dbt test
DBT_PROFILES_DIR=. dbt docs generate && DBT_PROFILES_DIR=. dbt docs serve
```

Model-level transformation documentation lives in
[dbt/models/docs.md](dbt/models/docs.md) and is rendered by `dbt docs serve`.

## License

MIT — see [LICENSE](LICENSE).
