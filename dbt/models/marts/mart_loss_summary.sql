-- Grain: one row per vintage_year. Drives the losses/liquidations dashboard
-- view (charter section 7: "basic loss/liquidation indicators").
--
-- A loan is counted as a liquidation event when its zero_balance_code is one
-- of Freddie Mac's credit-loss codes: 02 (third-party sale), 03 (short
-- sale/short payoff), or 09 (REO disposition). Codes such as 01
-- (prepaid/matured) and 06 (repurchase) are not credit losses and are
-- intentionally excluded — see dbt/models/docs.md for the full rationale.
with performance as (

    select * from {{ ref('fact_loan_performance') }}

),

loans as (

    select * from {{ ref('dim_loan') }}

),

liquidations as (

    select
        p.loan_identifier,
        p.current_actual_upb as balance_at_liquidation,
        p.actual_loss,
        p.net_sales_proceeds,
        p.mi_recoveries,
        p.non_mi_recoveries,
        p.total_expenses,
        l.vintage_year

    from performance as p
    inner join loans as l on p.loan_identifier = l.loan_identifier
    where p.zero_balance_code in ('02', '03', '09')

)

select
    vintage_year,
    count(distinct loan_identifier)               as liquidated_loan_count,
    sum(balance_at_liquidation)                    as total_balance_at_liquidation,
    sum(actual_loss)                               as total_actual_loss,
    sum(net_sales_proceeds)                        as total_net_sales_proceeds,
    sum(mi_recoveries)                             as total_mi_recoveries,
    sum(non_mi_recoveries)                         as total_non_mi_recoveries,
    sum(total_expenses)                            as total_expenses,
    sum(actual_loss) / nullif(sum(balance_at_liquidation), 0) as loss_severity
from liquidations
group by vintage_year
