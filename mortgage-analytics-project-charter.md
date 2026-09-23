# Project Charter: Mortgage Analytics Platform

**Version:** 2.0 (scope reduced for portfolio project)  
**Date:** September 23, 2026  
**Status:** Active  
**Owner:** Josiah Gordor (solo project)  
**Purpose of this document:** Personal data-engineering/analytics portfolio project, not a production or commercial product

> This charter was originally written as an enterprise-scale MVP proposal. It has been rescoped to
> what one person can realistically build, run, and demonstrate using free/sample public data, with
> the goal of showcasing an end-to-end pipeline: ingestion → cloud data warehouse → dbt data
> modeling → analysis, done well and documented, rather than covering many data sources or users.

## 1. Project purpose

Build an end-to-end mortgage analytics data pipeline — from raw public loan-level data to a
documented, tested canonical data model — that demonstrates practical data engineering and
analytics skills: cloud ingestion, a lakehouse bronze/staging/core architecture, dbt-managed
transformations, and reproducible loan-performance metrics.

The project focuses on single-family residential mortgage originations and monthly performance
using the Freddie Mac Single-Family Loan-Level Dataset sample files.

## 2. Problem this project demonstrates

Mortgage performance data is typically distributed across large flat files with cryptic headers
and inconsistent typing. This project shows how to:

- Land raw source files immutably and traceably (S3 → Databricks bronze)
- Standardize and type raw fields into a canonical schema (dbt staging/core layers)
- Produce basic, well-defined loan-performance metrics (delinquency, vintage, loss indicators)
- Document data lineage and transformation logic alongside the code that implements it

## 3. Objectives

1. Build a working ingestion pipeline for the Freddie Mac sample dataset (local files → S3 →
   Databricks bronze), with source lineage columns preserved. **Done.**
2. Build a canonical core data model (dimensions + fact) for loan origination and monthly
   performance, managed and tested with dbt. **Done.**
3. Compute a small set of practical loan-performance metrics (delinquency buckets, vintage/cohort
   segmentation, basic loss indicators) from the core model.
4. Document transformation logic, assumptions, and known limitations directly in the dbt project
   and README so the work is reviewable by someone unfamiliar with it.

### Stretch goals (optional, not required to consider the project complete)

- A lightweight analysis notebook or dashboard (e.g. a Jupyter notebook, Streamlit app, or BI tool
  connected to the core schema) presenting the metrics visually.
- Join to FHFA House Price Index data for a simple indexed-LTV or collateral-value enrichment
  example.
- Incremental/scheduled loads instead of full-refresh runs.

## 4. Scope

### In scope

- **Data:** Freddie Mac Single-Family Loan-Level Dataset — sample origination and monthly
  performance files only (not the full historical loan-level file, which is multiple GB per
  vintage and not necessary to demonstrate the architecture).
- **Pipeline:** local files → S3 → Databricks bronze (raw, typed as STRING) → dbt staging (typed,
  renamed) → dbt core (dimensional model).
- **Analytics:** loan count, current UPB, delinquency buckets and basic roll-up, vintage/cohort
  segmentation by LTV, credit score, geography, and origination period, and basic
  liquidation/loss indicators available directly from the performance fields.
- **Documentation:** README, project charter, and dbt-native model/column documentation.

### Out of scope

- Any other agency or macroeconomic data source (Fannie Mae, HMDA, FRED, BLS, Census, Ginnie Mae).
  These were part of the original enterprise proposal but add licensing, volume, and integration
  overhead disproportionate to a portfolio project.
- A multi-page dashboard suite, role-based access, or user-facing product.
- Scenario/stress testing, prepayment or credit-risk modeling beyond descriptive metrics.
- Any production, regulatory, or commercial use. This is a demonstration project using public
  sample data only.
- Personally identifiable information — the source dataset does not contain it, and none will be
  introduced.
- Formal governance process (steering group, change control, legal/compliance sign-off, staffing
  plan) — not applicable to a solo project.

## 5. Primary data source

| Source | Role | Notes |
|---|---|---|
| [Freddie Mac Single-Family Loan-Level Dataset](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset) | Sole data source: loan-level origination and monthly performance records | Public, registration required; sample files only, not redistributed beyond this repo's illustrative sample |

**Optional future addition:** [FHFA House Price Index](https://www.fhfa.gov/data/hpi/datasets) —
simple public CSV, no registration, useful for a follow-up geography/collateral-value exercise.

## 6. Requirements

### Functional

- Preserve raw source files and load metadata (`source_file`, `loaded_at`) through the bronze layer.
- Type and rename raw fields into a canonical schema (dbt staging layer).
- Build dimension and fact tables supporting vintage, geography, and monthly-performance analysis.
- Validate the model with automated tests (uniqueness, not-null, referential integrity).

### Non-functional

- **Reproducibility:** the same source files and code produce the same tables.
- **Documentation:** every core model has a description of its grain and transformations.
- **Simplicity over scale:** designed for a sample dataset (tens of thousands of records), not
  production loan-servicing volumes.

## 7. Metrics in scope

- Loan count and current unpaid principal balance
- Weighted-average original LTV/CLTV and credit score
- Delinquency buckets (Current / 30-59 / 60-89 / 90+ DPD / Closed)
- Vintage and cohort segmentation (origination year/quarter, state, LTV, credit score)
- Basic loss/liquidation indicators from zero-balance code and actual-loss fields

Formal numerator/denominator sign-off, weighting methodology, and stress scenarios from the
original enterprise version are not applicable here — metrics are descriptive and for
demonstration.

## 8. Status and milestones

1. ✅ Ingestion pipeline: sample files → S3 → Databricks bronze (`src/data_ingestion/`, `scripts/`)
2. ✅ dbt project with staging + core (dimensional) models and tests (`dbt/`)
3. ⬜ Exploratory analysis validating the metrics in section 7 against the core schema
4. ⬜ (Stretch) Lightweight notebook or dashboard presentation layer
5. ⬜ (Stretch) FHFA HPI join example

## 9. Assumptions and constraints

- Single developer, run locally against a personal AWS account and Databricks workspace.
- Uses Freddie Mac's public sample files, not the full historical release.
- Not intended for production, regulatory, or commercial use — for demonstration only.
- Freddie Mac's terms govern redistribution of the data itself; only small illustrative samples
  are kept in this repository.

## 10. Architecture principles

1. Preserve original files and source metadata.
2. Version code, schema mappings, and model assumptions in git.
3. Do not introduce personally identifiable information.
4. Favor transparent, reviewable calculations over opaque logic.
5. Keep source-specific ingestion code separate from the canonical dbt model.
6. Test and document the model as it's built, not as an afterthought.
5. Which user groups will participate in MVP acceptance testing?
6. What portfolio population and observation period define the first release?
7. Which metrics are launch-critical?
8. What are the approved refresh frequency and data-retention periods?
9. What export and redistribution controls are required?
10. What budget, staffing, and target launch date are authorized?

## 20. Charter approval

Approval indicates agreement with the project purpose, initial scope, governance model, constraints, and Phase 0 deliverables. It does not authorize use of any dataset beyond terms approved by legal, compliance, privacy, or the relevant data owner.

| Role | Name | Decision | Date |
|---|---|---|---|
| Executive sponsor |  | Approve / Revise |  |
| Product owner |  | Approve / Revise |  |
| Risk/analytics lead |  | Approve / Revise |  |
| Data/technology lead |  | Approve / Revise |  |
| Legal/compliance reviewer |  | Approve / Revise |  |
| Information-security reviewer |  | Approve / Revise |  |

## Appendix: Initial source links

- Freddie Mac Single-Family Loan-Level Dataset: https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset
- Fannie Mae Single-Family Loan Performance Data: https://capitalmarkets.fanniemae.com/credit-risk-transfer/single-family-credit-risk-transfer/fannie-mae-single-family-loan-performance-data
- CFPB HMDA Data: https://www.consumerfinance.gov/data-research/hmda/
- HMDA File-Serving API Documentation: https://ffiec.cfpb.gov/documentation/api/file-serving/
- FHFA House Price Index Datasets: https://www.fhfa.gov/data/hpi/datasets
- Ginnie Mae Disclosure Data Download: https://bulk.ginniemae.gov/
- Census ACS API: https://www.census.gov/programs-surveys/acs/data/data-via-api.html
- FRED: https://fred.stlouisfed.org/
- BLS API: https://www.bls.gov/bls/api_features.htm
- Federal Reserve charge-off and delinquency data: https://www.federalreserve.gov/releases/chargeoff/
