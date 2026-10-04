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
        │  dbt (dbt/)
        ▼
Databricks marts schema (dashboard-ready summary tables)
```

`airflow/dags/mortgage_analytics_pipeline_dag.py` (dag_id `mortgage_analytics_pipeline`)
orchestrates the full chain above (S3 upload → bronze load → dbt run → dbt
test) so new files dropped under `data/` flow through to the marts/dashboard
layer automatically.

## Project structure

```
config/config.yaml         Non-secret settings (AWS bucket/region, Databricks catalog/schema)
data/                       Sample Freddie Mac origination and performance files, plus headers
src/data_ingestion/         Python ingestion library (S3 upload, Databricks bronze load)
scripts/                    Thin CLI entry points that call the ingestion library
dbt/                        dbt project: staging + core/marts models, macros, tests, docs
airflow/dags/               Airflow DAG orchestrating the end-to-end pipeline
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

## Orchestration (Airflow)

`airflow/dags/mortgage_analytics_pipeline_dag.py` (dag_id `mortgage_analytics_pipeline`)
runs the full pipeline (upload to S3 → load Databricks bronze → `dbt run` →
`dbt test`) on a 15-minute schedule, but short-circuits (skips) unless a file
under `data/` is newer than the last successfully processed run — an mtime
watermark stored in an Airflow Variable, since this project polls local files
rather than wiring up real S3 event notifications.

Airflow is intentionally not pinned in `requirements.txt` and must NOT be
installed into the project's `.venv` — its pinned dependencies (protobuf,
jinja2, babel, etc.) downgrade packages that `dbt-databricks` needs and will
break `dbt` in that environment. Install Airflow into its own venv instead;
the DAG invokes `dbt` via an absolute path to `.venv/bin/dbt`, so the two
environments never need to overlap.

```bash
python3 -m venv .venv-airflow
source .venv-airflow/bin/activate

AIRFLOW_VERSION=2.9.3
PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
pip install boto3 python-dotenv PyYAML databricks-sql-connector databricks-sdk

export AIRFLOW_HOME="$(pwd)/airflow"
airflow standalone
```

`airflow standalone` creates an admin user (see
`airflow/standalone_admin_password.txt`) and serves the UI at
http://localhost:8080, where the `mortgage_analytics_pipeline` DAG can be
unpaused and triggered. To run it once from the CLI instead (no
webserver/scheduler needed):

```bash
export AIRFLOW_HOME="$(pwd)/airflow"
airflow db migrate
airflow dags test mortgage_analytics_pipeline "$(date +%F)"
```

`AIRFLOW_HOME` is only set for the current shell session — export it again in
every new terminal before running any `airflow` command, otherwise it
silently falls back to the default `~/airflow` (a different, uninitialized
metadata DB and DAGs folder).

## License

MIT — see [LICENSE](LICENSE).

