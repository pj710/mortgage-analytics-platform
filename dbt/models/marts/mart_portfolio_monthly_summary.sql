-- Grain: one row per (period_date, delinquency_bucket). Drives the
-- portfolio-overview and delinquency-trend dashboard views (charter section 7:
-- "loan count and current unpaid principal balance", "delinquency buckets").
with performance as (

    select * from {{ ref('fact_loan_performance') }}

),

period as (

    select * from {{ ref('dim_period') }}

)

select
    f.period_date,
    p.period_year,
    p.period_quarter,
    p.period_label,
    f.delinquency_bucket,
    count(distinct f.loan_identifier)                                     as loan_count,
    sum(f.current_actual_upb)                                             as total_current_upb,
    {{ weighted_average('f.current_interest_rate', 'f.current_actual_upb') }} as wa_current_interest_rate
from performance as f
inner join period as p on f.period_date = p.period_date
group by f.period_date, p.period_year, p.period_quarter, p.period_label, f.delinquency_bucket
