{{ config(materialized='view') }}

-- Grain: one row per loan_identifier — its most recent monthly performance
-- snapshot. Used by marts that need a loan's current status rather than its
-- full performance history (e.g. geography and portfolio point-in-time views).
with performance as (

    select
        *,
        row_number() over (
            partition by loan_identifier
            order by period_date desc
        ) as row_num

    from {{ ref('fact_loan_performance') }}

)

select
    loan_identifier,
    period_date,
    current_actual_upb,
    current_interest_rate,
    delinquency_bucket,
    zero_balance_code
from performance
where row_num = 1
