# Project Charter: Mortgage Analytics Platform

**Version:** 1.0  
**Date:** September 12, 2026  
**Status:** Draft for approval  
**Project sponsor:** To be assigned  
**Project manager/product owner:** To be assigned  
**Target MVP:** Approximately 16–20 weeks after approval

## 1. Project purpose

Develop a U.S. residential mortgage analytics platform and dashboard for analyzing loan performance, identifying emerging credit and prepayment risk, supporting portfolio surveillance, and evaluating stress scenarios using approved public mortgage, housing-market, geographic, and macroeconomic data.

The initial release will focus on single-family residential mortgages and provide transparent, reproducible analytics rather than opaque model outputs.

## 2. Business problem

Mortgage performance data is distributed across large files, APIs, and agency disclosure systems. Analysts often manually combine origination, servicing-performance, property-market, geographic, and economic data before answering basic risk questions.

The platform will:

- Centralize approved public data sources
- Standardize mortgage and performance fields
- Make portfolio trends and risk concentrations visible
- Reduce manual spreadsheet analysis
- Provide repeatable delinquency, loss, prepayment, and vintage analysis
- Support transparent stress testing and auditability

## 3. Vision

Provide a trusted mortgage-risk workspace where users can move from portfolio-level trends to loan segments, geographies, and economic drivers in minutes, with every result traceable to source data and a documented methodology.

## 4. Objectives

### Primary objectives

1. Build reliable ingestion and data-quality pipelines for public mortgage datasets.
2. Create a canonical data model for loan origination, monthly performance, liquidation, geography, house prices, and economic indicators.
3. Deliver an MVP dashboard for portfolio monitoring and risk segmentation.
4. Enable vintage and cohort analysis across loan, borrower, property, and geographic characteristics.
5. Estimate collateral-value changes and indexed current LTV using public house-price data.
6. Add transparent scenario analysis for house prices, unemployment, interest rates, and performance transitions.
7. Establish data lineage, licensing controls, model documentation, and reproducible calculations.

### Secondary objectives

- Create a foundation for future client or proprietary portfolio data
- Support explainable credit-risk and prepayment models
- Provide exportable tables and charts for approved users
- Establish a reusable framework for adding Fannie Mae, Ginnie Mae, FHA, VA, and USDA datasets

## 5. Scope

### In scope for the MVP

#### Data

- Freddie Mac Single-Family Loan-Level Dataset as the primary performance source
- Fannie Mae Single-Family Loan Performance Data, subject to access and licensing approval
- CFPB/FFIEC HMDA data for origination and market benchmarking
- FHFA House Price Index data for collateral-market enrichment
- FRED, BLS, and Federal Reserve macroeconomic series
- Census ACS and geographic reference data where needed

#### Analytics

- Portfolio balance and loan-count metrics
- Delinquency buckets and roll rates
- Cure, default, liquidation, loss, and recovery metrics
- Prepayment and runoff analysis
- Vintage and cohort analysis
- Risk segmentation by LTV, credit score, DTI, purpose, occupancy, product, geography, and origination period, subject to field availability
- Indexed property-value and estimated-current-LTV analysis
- Geographic concentration and performance analysis
- Basic stress testing
- Data-quality and freshness monitoring

#### User experience

- Executive portfolio overview
- Performance-monitoring dashboard
- Vintage/cohort dashboard
- Risk-segmentation dashboard
- Geographic and collateral dashboard
- Prepayment dashboard
- Loss and recovery dashboard
- Scenario-analysis dashboard
- Filters, saved views, source notes, and exportable results

#### Governance and operations

- Data dictionary and source catalog
- Data lineage from source file to dashboard metric
- Dataset versioning and refresh history
- Validation and reconciliation reports
- Role-based access for the MVP
- Documentation of assumptions and known limitations

### Out of scope for the MVP

- Production use as a regulated credit-decisioning system
- Individual borrower underwriting or automated approval/decline decisions
- Personally identifiable information or borrower identity resolution
- Servicing workflow execution, collections, or borrower communications
- Real-time loan-servicing integration
- Full private-label securitization coverage
- Formal regulatory model validation or regulatory capital calculations
- Automated investment, trading, or hedging recommendations
- Guaranteed property valuations or appraisal replacement
- Commercial redistribution of restricted agency datasets without explicit permission
- Advanced deep-learning models before baseline analytics are validated

## 6. Target users and stakeholders

| Group | Primary needs | Involvement |
|---|---|---|
| Executive sponsor | Business value, budget, risk acceptance | Approves charter, scope, and major changes |
| Product owner/project manager | Prioritization and delivery coordination | Owns backlog and acceptance |
| Portfolio managers | Trends, concentrations, runoff, scenarios | Defines use cases and validates dashboards |
| Credit-risk analysts | Delinquencies, defaults, losses, segmentation | Defines metrics and validates results |
| Servicing/operations analysts | Watchlists and early-warning indicators | Provides workflow requirements |
| Data engineering | Ingestion, transformation, storage, monitoring | Builds data platform |
| Analytics/modeling | Metrics, models, stress tests | Builds analytical layer |
| BI/front-end | Dashboard interaction and usability | Builds user interface |
| Legal/compliance/privacy | Data use, licensing, and governance | Approves sources and controls |
| Information security | Access, auditability, and environment controls | Reviews architecture and controls |

## 7. Product deliverables

1. Approved requirements and metric specification
2. Public-data source catalog with URLs, coverage, update frequency, schema, and licensing notes
3. Raw data landing zone with immutable source files and checksums
4. Canonical mortgage data model
5. Ingestion and transformation pipelines
6. Data-quality framework
7. Analytics layer for portfolio, delinquency, prepayment, loss, vintage, and scenario metrics
8. MVP dashboard application
9. Data dictionary and methodology guide
10. User and administrator documentation
11. Testing and validation report
12. Production-readiness and operating-runbook package

### MVP dashboard pages

- Portfolio Overview
- Performance Monitoring
- Vintage and Cohort Analysis
- Risk Segmentation
- Geography and Collateral
- Prepayments and Runoff
- Losses and Recoveries
- Scenario Analysis
- Data Quality and Source Lineage

## 8. Initial public data sources

| Source | Platform role | Key considerations |
|---|---|---|
| [Freddie Mac Single-Family Loan-Level Dataset](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset) | Primary loan-level origination and monthly performance data | Registration required; commercial redistribution is subject to terms |
| [Fannie Mae Single-Family Loan Performance Data](https://capitalmarkets.fanniemae.com/credit-risk-transfer/single-family-credit-risk-transfer/fannie-mae-single-family-loan-performance-data) | Supplemental conventional performance benchmark | Registration and external-use restrictions may apply |
| [CFPB/FFIEC HMDA](https://www.consumerfinance.gov/data-research/hmda/) | Applications, originations, borrower/property characteristics, lender and geography benchmarking | Public, privacy-protected; not a servicing-performance dataset |
| [FHFA House Price Index](https://www.fhfa.gov/data/hpi/datasets) | Regional collateral-price trends and indexed current-value estimates | Estimates are not appraisals |
| [FRED](https://fred.stlouisfed.org/) and Federal Reserve series | Rates, unemployment, delinquency, charge-offs, and economic context | Track definitions and revisions |
| [BLS API](https://www.bls.gov/bls/api_features.htm) | Unemployment, CPI, employment, and labor-market data | Preserve release vintage where backtesting requires it |
| [Census ACS API](https://www.census.gov/programs-surveys/acs/data/data-via-api.html) and TIGER/Line | Demographic, income, housing, and geographic enrichment | Use compatible periods and crosswalks |
| [Ginnie Mae disclosures](https://bulk.ginniemae.gov/) | Future government-loan and MBS analytics | Large files and source-specific layouts; add after MVP foundation |

All source access, storage, transformation, display, retention, and redistribution rights must be reviewed before production use. Restricted source data must not be exposed through unrestricted downloads or external-facing interfaces.

## 9. High-level requirements

### Functional

- Ingest source files and APIs on a documented schedule.
- Preserve raw source data and processing metadata.
- Normalize source-specific fields into a canonical schema.
- Calculate monthly and cumulative performance metrics.
- Support filtering and grouping by approved dimensions.
- Compare vintages and cohorts consistently.
- Join mortgage data to time-series and geographic data.
- Run documented baseline stress scenarios.
- Show data freshness and source lineage for dashboard results.
- Export approved aggregate results without violating source restrictions.
- Support user roles and access controls.

### Non-functional

- **Reproducibility:** The same source version and configuration produces the same result.
- **Auditability:** Headline metrics are traceable to definitions and source releases.
- **Performance:** Common cached dashboard views target a five-second-or-less load time.
- **Scalability:** The architecture supports tens of millions of loans and hundreds of millions of performance records.
- **Security:** Apply least privilege, encryption, secrets management, and audit logging.
- **Usability:** A trained analyst can answer common portfolio questions without writing SQL.
- **Accessibility:** Follow applicable internal accessibility standards for charts, tables, filters, and color use.

## 10. Initial metric dictionary

The following metrics require formal approval of numerator, denominator, observation date, exclusions, missing-value treatment, and weighting method:

- Loan count
- Current unpaid principal balance
- Weighted-average coupon
- Weighted-average original LTV and current indexed LTV
- 30-, 60-, and 90-plus-day delinquency rates
- Serious-delinquency rate
- Roll rates between delinquency states
- Cure rate
- Voluntary prepayment and conditional prepayment rates, where supported
- Default or liquidation rate
- Gross and net loss
- Loss severity
- Recovery rate
- Average time to liquidation
- Portfolio runoff
- Concentration by geography, product, vintage, LTV, credit score, and purpose
- Incremental loss under defined stress scenarios

## 11. Delivery approach and milestones

### Phase 0: Charter and discovery — Weeks 1–2

- Approve charter and success criteria
- Confirm sponsor, product owner, and core team
- Confirm internal versus commercial-use objective
- Complete source-access and licensing review
- Prioritize dashboard use cases
- Approve initial metric dictionary
- Produce architecture decision record

**Exit criteria:** Approved scope, named decision-makers, source-use plan, and prioritized MVP backlog.

### Phase 1: Data foundation — Weeks 3–8

- Set up raw and curated storage
- Implement Freddie Mac ingestion
- Implement HMDA ingestion
- Implement FHFA HPI ingestion
- Implement macroeconomic-series ingestion
- Build canonical schema and source mappings
- Add data-quality checks and reconciliation reports
- Create data catalog and lineage metadata

**Exit criteria:** Repeatable pipelines produce validated curated tables for selected source periods.

### Phase 2: Analytics MVP — Weeks 9–12

- Implement portfolio KPIs
- Implement delinquency and roll-rate calculations
- Implement vintage and cohort analysis
- Implement prepayment and loss metrics
- Implement geography and HPI enrichment
- Validate results against source documentation and independent calculations

**Exit criteria:** Metric validation report is approved by risk and analytics stakeholders.

### Phase 3: Dashboard MVP — Weeks 13–16

- Build dashboard navigation and filtering
- Implement overview, performance, vintage, risk, geography, prepayment, and loss views
- Add source notes, freshness indicators, and export controls
- Conduct usability testing with representative users

**Exit criteria:** User acceptance testing passes for priority workflows.

### Phase 4: Scenario analysis and production hardening — Weeks 17–20

- Implement HPI, unemployment, and interest-rate scenarios
- Add scenario comparison and result explanations
- Complete access control, monitoring, documentation, and runbooks
- Perform security and performance review
- Conduct MVP launch-readiness review

**Exit criteria:** Production-readiness checklist is approved and the MVP is released to pilot users.

## 12. Success criteria

The MVP will be successful when it can:

1. Load and validate the selected public datasets on a repeatable schedule.
2. Process a representative large performance sample without manual spreadsheet intervention.
3. Produce approved delinquency, prepayment, loss, recovery, and vintage metrics.
4. Segment results by at least five core dimensions, including vintage, geography, LTV, credit score, and loan purpose where available.
5. Join loan or cohort data to FHFA HPI and selected macroeconomic series.
6. Reproduce defined validation totals within approved tolerances.
7. Display freshness, source, release period, and methodology for each major dashboard section.
8. Complete common analyst workflows in minutes rather than hours.
9. Pass privacy, licensing, security, and user-acceptance reviews.
10. Document known data limitations and prevent unauthorized raw-data redistribution.

Suggested initial targets:

- At least 95% automated pipeline success for scheduled refreshes
- At least 98% completeness for required keys and reporting periods
- 100% of headline KPIs linked to documented definitions
- At least 90% pass rate for priority user-acceptance scenarios
- Zero unresolved critical licensing or privacy issues at launch

## 13. Assumptions

- The initial deployment is internal-only or otherwise approved for its intended use.
- Public datasets will be accessed under their current terms and may change.
- The initial platform uses historical or periodically refreshed data, not real-time servicing feeds.
- Public loan-level datasets do not represent the entire U.S. mortgage market.
- The first release prioritizes conventional single-family mortgages.
- Geographic joins require crosswalks and carry estimation uncertainty.
- Indexed property values are analytical estimates, not underwriting values or appraisals.
- Users approve definitions of delinquency, default, loss, prepayment, and portfolio population before release.

## 14. Constraints

- Large source files require columnar storage and optimized processing rather than spreadsheets.
- Agency datasets may require registration, usage agreements, and redistribution restrictions.
- Source schemas and historical data may be corrected or revised.
- HMDA and other public datasets have privacy-protection and aggregation limitations.
- Desired attributes may be unavailable, masked, or inconsistent across sources.
- Hosting environment, security classification, budget, and staffing remain to be confirmed.

## 15. Key risks and responses

| Risk | Impact | Likelihood | Response |
|---|---|---:|---|
| Dataset licensing restrictions prevent intended distribution | High | Medium | Complete legal review before ingestion; design export controls around approved use |
| Public datasets do not represent the target portfolio | High | Medium | Label benchmark populations clearly; add proprietary feeds later |
| Large files create slow or unreliable processing | High | High | Use object storage, Parquet, partitioning, incremental loads, and aggregate queries |
| Source schema or release changes break pipelines | High | Medium | Version schemas, maintain contract tests, monitor files, and retain prior releases |
| Metric definitions differ across teams | High | Medium | Approve a shared metric dictionary and validation suite before UAT |
| Geography crosswalks distort current-LTV estimates | Medium | Medium | Document crosswalks, use compatible geography levels, and present limitations |
| Model outputs are misunderstood as decisions | High | Medium | Explain assumptions, show ranges, and prohibit automated credit decisions in MVP |
| Restricted data is exported improperly | High | Low/Medium | Apply role-based access, aggregation thresholds, download controls, and audit logs |
| Dashboard adoption is low | Medium | Medium | Test with analysts early and prioritize recurring workflows |
| Delivery expands beyond MVP | Medium | High | Use change control and maintain a prioritized backlog |

## 16. Governance and decision rights

### Steering group

The sponsor, product owner, risk lead, data lead, and technology lead will meet at least biweekly during delivery.

Responsibilities:

- Approve scope and priority changes
- Resolve cross-functional conflicts
- Approve major architecture and source decisions
- Review delivery risks and budget
- Approve MVP launch

### Product owner/project manager

Owns the backlog, metric and dashboard priorities, acceptance criteria, user feedback, and release decisions.

### Risk and analytics lead

Owns metric definitions, analytical methods, model assumptions, validation, and interpretation.

### Data and technology lead

Owns architecture, pipeline reliability, storage, performance, security implementation, and technical documentation.

### Legal, compliance, privacy, and security reviewers

Must approve relevant data-use, privacy, access, retention, and redistribution controls before production release.

### Change control

Changes affecting launch date, approved data sources, legal terms, user population, security posture, or budget require documented impact analysis and steering-group approval.

## 17. Initial team structure

- Executive sponsor
- Product owner/project manager
- Mortgage-risk subject-matter expert
- Data architect or data engineer
- Analytics/modeling lead
- BI or front-end engineer
- QA/data-quality engineer
- Platform/DevOps engineer, initially part time
- Legal/compliance/privacy reviewer, part time
- Information-security reviewer, part time

The staffing plan and budget will be established during Phase 0.

## 18. Architecture principles

1. Preserve original files and source metadata.
2. Version code, mappings, definitions, and model assumptions.
3. Do not introduce personally identifiable information into the MVP.
4. Track permissions at the dataset and output level.
5. Favor transparent calculations and interpretable models.
6. Keep source adapters separate from the canonical model.
7. Process new releases incrementally where practical.
8. Reconcile aggregate results and test edge cases before publication.
9. Apply least privilege and controlled exports.
10. Support future proprietary portfolio feeds without redesigning the analytical layer.

## 19. Approval decisions required

1. Who is the executive sponsor and product owner?
2. Is the initial product internal-only, research-only, or intended for commercial use?
3. Which agency datasets are approved for initial deployment?
4. What hosting environment and security classification apply?
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
