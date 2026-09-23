-- Grain: one row per (loan_identifier, period_date) monthly performance snapshot.
-- Inner-joined to dim_loan so only performance records with a matching
-- origination record are kept (charter architecture principle 8: reconcile
-- aggregate results and test edge cases before publication).
with performance as (

    select * from {{ ref('stg_performance') }}

),

loans as (

    select loan_identifier from {{ ref('dim_loan') }}

)

select
    p.loan_identifier,
    p.period_date,
    p.current_actual_upb,
    p.current_interest_rate,
    p.current_non_interest_bearing_upb,
    p.loan_age_months,
    p.remaining_months_to_maturity,
    p.delinquency_months,
    {{ delinquency_bucket('p.delinquency_months', 'p.zero_balance_code') }} as delinquency_bucket,
    p.modification_flag,
    p.zero_balance_code,
    p.zero_balance_effective_date,
    p.estimated_ltv,
    p.mi_recoveries,
    p.net_sales_proceeds,
    p.non_mi_recoveries,
    p.total_expenses,
    p.legal_costs,
    p.maintenance_and_preservation_costs,
    p.taxes_and_insurance,
    p.miscellaneous_expenses,
    p.actual_loss,
    p.cumulative_modification_costs,
    p.current_period_modification_costs,
    p.payment_deferral_flag,
    p.delinquency_due_to_disaster,
    p.borrower_assistance_plan,
    p.servicer_name
from performance as p
inner join loans as l on p.loan_identifier = l.loan_identifier
