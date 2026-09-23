-- Grain: one row per property_state. Drives the geography/concentration
-- dashboard view (charter section 7 / in-scope analytics: risk segmentation
-- and concentration by geography). Current-status columns come from each
-- loan's most recent snapshot (int_loan_latest_snapshot), not its full history.
with loans as (

    select * from {{ ref('dim_loan') }}

),

geography as (

    select * from {{ ref('dim_geography') }}

),

latest_snapshot as (

    select * from {{ ref('int_loan_latest_snapshot') }}

)

select
    coalesce(g.property_state, 'UNKNOWN')                                as property_state,
    count(distinct l.loan_identifier)                                    as loan_count,
    sum(l.original_upb)                                                  as total_original_upb,
    {{ weighted_average('l.original_ltv', 'l.original_upb') }}           as wa_original_ltv,
    {{ weighted_average('l.credit_score', 'l.original_upb') }}          as wa_credit_score,
    sum(coalesce(s.current_actual_upb, 0))                               as total_current_upb,
    count(distinct case when s.delinquency_bucket = '90+ DPD' then l.loan_identifier end)
        as loans_90_plus_dpd,
    count(distinct case when s.delinquency_bucket = '90+ DPD' then l.loan_identifier end)
        / nullif(count(distinct s.loan_identifier), 0)                   as serious_delinquency_rate
from loans as l
left join geography as g on l.property_state = g.property_state
left join latest_snapshot as s on l.loan_identifier = s.loan_identifier
group by coalesce(g.property_state, 'UNKNOWN')
