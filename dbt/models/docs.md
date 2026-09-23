{% docs bronze_sources %}
Bronze tables are the raw landing zone loaded by `src/data_ingestion/load_s3_to_databricks.py`
via Databricks `COPY INTO` from the Freddie Mac Single-Family Loan-Level sample files in S3.
Every source field lands as `STRING` with no type conversion, plus `source_file` and `loaded_at`
lineage columns, per project-charter architecture principle 1 ("Preserve original files and
source metadata").
{% enddocs %}

{% docs stg_originations %}
Staging model over `bronze.originations_raw`. One row per source record (one record expected
per loan). Transformations applied:

- Casts numeric fields (FICO, VantageScore, LTV/CLTV/DTI, UPB, interest rate, loan term,
  unit/borrower counts) from `STRING` to numeric types with `try_cast`, so malformed values
  become `NULL` instead of failing the run.
- Parses `first_payment_date` and `maturity_date` from Freddie Mac's `YYYYMM` string format into
  `DATE` values (assumed day 1 of month).
- Renames raw header-derived columns to canonical, descriptive snake_case names used everywhere
  downstream.

Supports charter objective 2, "canonical data model for loan origination."
{% enddocs %}

{% docs stg_performance %}
Staging model over `bronze.performance_raw`. One row per loan per monthly reporting period.
Transformations applied:

- Casts monetary and rate fields from `STRING` to `DECIMAL`/numeric types with `try_cast`.
- Parses the raw `period` (`YYYYMM`) into `period_date` plus `period_year`/`period_month`
  integers.
- Normalizes `current_loan_delinquency_status` into a nullable integer `delinquency_months`.
  Freddie Mac uses non-numeric codes (`R`, `RA`, `XX`) for repurchased, restarted, or unreported
  status; these are mapped to `NULL` rather than guessed at or dropped.
- Preserves `zero_balance_code` and `zero_balance_effective_date` for downstream
  liquidation/loss logic.

Supports charter objective 2, "canonical data model for ... monthly performance."
{% enddocs %}

{% docs dim_loan %}
Grain: one row per `loan_identifier`. Built from `stg_originations`, defensively deduplicated by
keeping the most recently loaded record per loan (`row_number()` over `loaded_at`).

Adds derived vintage attributes (`vintage_year`, `vintage_quarter`, `vintage_label`) from
`first_payment_date` to support the charter's vintage/cohort analysis objective and risk
segmentation by LTV, credit score, DTI, purpose, occupancy, product, and geography (charter
section 5, "Analytics").
{% enddocs %}

{% docs dim_geography %}
Grain: one row per distinct (`property_state`, `msa_code`, `postal_code`) combination observed in
originations. `geography_key` is a SHA-256 hash surrogate key so the dimension can be joined
consistently even where a natural key column is null. Intended as the join point for future FHFA
HPI and Census enrichment (charter sections 5 and 8), which are out of scope for this load.
{% enddocs %}

{% docs dim_period %}
Grain: one row per distinct reporting `period_date` observed in performance data — not a full
calendar spine, since only the loaded sample periods are represented. Adds `period_quarter` and
`period_label` for reporting convenience.
{% enddocs %}

{% docs fact_loan_performance %}
Grain: one row per (`loan_identifier`, `period_date`) monthly performance snapshot, inner-joined
to `dim_loan` so only performance records with a matching origination record are kept
(referential integrity per charter architecture principle 8, "reconcile aggregate results and
test edge cases before publication").

Adds `delinquency_bucket` (Current / 30-59 DPD / 60-89 DPD / 90+ DPD / Closed / Unknown), derived
via the shared `delinquency_bucket()` macro from `delinquency_months` and `zero_balance_code`, to
directly support the charter's delinquency-bucket and roll-rate metrics (charter section 10).
{% enddocs %}
