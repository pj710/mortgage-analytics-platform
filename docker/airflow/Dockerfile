# Custom Airflow image for the mortgage analytics pipeline.
#
# Mirrors the local (non-Docker) .venv / .venv-airflow split documented in
# README.md: dbt-databricks's pinned dependencies conflict with Airflow's, so
# dbt is installed into its own virtualenv inside the image instead of
# Airflow's environment. The DAG is pointed at that venv via the DBT_BIN
# environment variable (see docker/docker-compose.yaml).
FROM apache/airflow:2.9.3-python3.9

# Packages imported directly by the DAG's Python tasks (S3 upload, Databricks
# bronze load) -- these must live in Airflow's own environment.
COPY docker/airflow/requirements-airflow.txt /tmp/requirements-airflow.txt
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.9.txt" \
    -r /tmp/requirements-airflow.txt

USER root
COPY docker/airflow/requirements-dbt.txt /tmp/requirements-dbt.txt
RUN python3 -m venv /opt/dbt-venv \
    && /opt/dbt-venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/dbt-venv/bin/pip install --no-cache-dir -r /tmp/requirements-dbt.txt \
    && chown -R airflow:root /opt/dbt-venv
USER airflow
