-- Grain: one row per reporting period actually observed in the performance
-- data (not a full calendar spine), since only the loaded sample periods exist.
with periods as (

    select distinct
        period_date,
        period_year,
        period_month
    from {{ ref('stg_performance') }}
    where period_date is not null

)

select
    period_date,
    period_year,
    period_month,
    quarter(period_date)                                as period_quarter,
    concat('Q', quarter(period_date), ' ', period_year) as period_label
from periods
