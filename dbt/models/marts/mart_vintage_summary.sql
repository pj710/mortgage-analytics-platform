-- Grain: one row per (vintage_year, vintage_quarter). Drives the
-- vintage/cohort-analysis dashboard view (charter section 7: "vintage and
-- cohort segmentation", "weighted-average original LTV/CLTV and credit score").
with loans as (

    select * from {{ ref('dim_loan') }}

)

select
    vintage_year,
    vintage_quarter,
    vintage_label,
    count(*)                                                          as loan_count,
    sum(original_upb)                                                 as total_original_upb,
    {{ weighted_average('original_ltv', 'original_upb') }}            as wa_original_ltv,
    {{ weighted_average('original_cltv', 'original_upb') }}           as wa_original_cltv,
    {{ weighted_average('credit_score', 'original_upb') }}            as wa_credit_score,
    {{ weighted_average('original_interest_rate', 'original_upb') }}  as wa_original_interest_rate
from loans
group by vintage_year, vintage_quarter, vintage_label
