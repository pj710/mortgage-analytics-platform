"""Process new Freddie Mac raw data through S3 -> Databricks bronze -> dbt core/marts.

"Process once uploaded" is approximated with an mtime watermark stored in an
Airflow Variable (polled on a schedule) rather than a true S3/file event
trigger -- see mortgage-analytics-project-charter.md for why simplicity was
chosen over an event-driven design for this portfolio project.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag, task
from airflow.models import Variable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DBT_DIR = PROJECT_ROOT / "dbt"
# dbt-databricks pins conflict with Airflow's deps, so dbt lives in its own
# venv (.venv) instead of whatever env is running Airflow (.venv-airflow).
DBT_BIN = PROJECT_ROOT / ".venv" / "bin" / "dbt"
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from data_ingestion.ingest import find_files, get_settings as get_ingest_settings  # noqa: E402
from data_ingestion.load_s3_to_databricks import load_s3_to_bronze  # noqa: E402

WATERMARK_VAR = "mortgage_analytics_pipeline_last_processed_mtime"
PENDING_WATERMARK_VAR = f"{WATERMARK_VAR}_pending"


def _dbt_env():
    """dbt env vars come from .env, which uses 'KEY = VALUE' spacing bash can't source directly."""
    import dotenv

    env = dict(os.environ)
    for key, value in dotenv.dotenv_values(PROJECT_ROOT / ".env").items():
        if value:
            env[key] = value.strip()
    env["DBT_PROFILES_DIR"] = "."
    return env


def _run_dbt(*args):
    result = subprocess.run(
        [str(DBT_BIN), *args], cwd=str(DBT_DIR), env=_dbt_env(), capture_output=True, text=True
    )
    print(result.stdout)
    print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"dbt {' '.join(args)} failed (exit {result.returncode})")


@dag(
    dag_id="mortgage_analytics_pipeline",
    description="Process incoming Freddie Mac raw data into the Databricks bronze/core/marts dashboard layer.",
    schedule_interval="@yearly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["mortgage-analytics"],
)
def mortgage_analytics_pipeline():

    @task.short_circuit
    def check_for_new_data():
        """Skip the rest of the DAG if no data file is newer than the last processed watermark."""
        data_root, _, _, _ = get_ingest_settings()
        files = find_files(data_root)
        if not files:
            return False

        latest_mtime = max(f.stat().st_mtime for f in files)
        last_processed = float(Variable.get(WATERMARK_VAR, default_var=0))
        if latest_mtime <= last_processed:
            return False

        Variable.set(PENDING_WATERMARK_VAR, latest_mtime)
        return True

    @task
    def upload_to_s3():
        from data_ingestion import load_to_s3

        load_to_s3()

    @task
    def load_bronze():
        load_s3_to_bronze()

    @task
    def dbt_run():
        _run_dbt("run")

    @task
    def dbt_test():
        _run_dbt("test")

    @task
    def record_watermark():
        """Promote the pending mtime to the real watermark now that the run succeeded end to end."""
        pending = Variable.get(PENDING_WATERMARK_VAR, default_var=None)
        if pending is not None:
            Variable.set(WATERMARK_VAR, pending)

    gate = check_for_new_data()
    uploaded = upload_to_s3()
    bronze = load_bronze()
    ran = dbt_run()
    tested = dbt_test()
    watermark = record_watermark()

    gate >> uploaded >> bronze >> ran >> tested >> watermark


mortgage_analytics_pipeline()
