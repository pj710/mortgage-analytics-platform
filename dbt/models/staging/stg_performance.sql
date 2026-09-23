with source as (

    select * from {{ source('bronze', 'performance_raw') }}

),

renamed as (

    select
        loan_identifier,
        to_date(period || '01', 'yyyyMMdd')                                as period_date,
        try_cast(substr(period, 1, 4) as int)                              as period_year,
        try_cast(substr(period, 5, 2) as int)                              as period_month,
        try_cast(current_actual_upb as decimal(18, 2))                    as current_actual_upb,
        current_loan_delinquency_status,
        -- Freddie Mac uses non-numeric codes ('R'/'RA'/'XX') for repurchased,
        -- restarted, or unreported status; normalize those to NULL rather than
        -- guessing a delinquency bucket for them.
        case
            when current_loan_delinquency_status = '0' then 0
            when current_loan_delinquency_status rlike '^[0-9]+$'
                then try_cast(current_loan_delinquency_status as int)
            else null
        end                                                                 as delinquency_months,
        try_cast(loan_age as int)                                         as loan_age_months,
        try_cast(remaining_months_to_legal_maturity as int)               as remaining_months_to_maturity,
        modification_flag,
        nullif(zero_balance_code, '')                                     as zero_balance_code,
        to_date(nullif(zero_balance_effective_date, '') || '01', 'yyyyMMdd') as zero_balance_effective_date,
        try_cast(current_interest_rate as decimal(8, 3))                 as current_interest_rate,
        try_cast(current_non_interest_bearing_upb as decimal(18, 2))     as current_non_interest_bearing_upb,
        try_cast(mi_recoveries as decimal(18, 2))                        as mi_recoveries,
        try_cast(net_sales_proceeds as decimal(18, 2))                   as net_sales_proceeds,
        try_cast(non_mi_recoveries as decimal(18, 2))                    as non_mi_recoveries,
        try_cast(total_expenses as decimal(18, 2))                       as total_expenses,
        try_cast(legal_costs as decimal(18, 2))                          as legal_costs,
        try_cast(maintenance_and_preservation_costs as decimal(18, 2))   as maintenance_and_preservation_costs,
        try_cast(taxes_and_insurance as decimal(18, 2))                  as taxes_and_insurance,
        try_cast(miscellaneous_expenses as decimal(18, 2))               as miscellaneous_expenses,
        try_cast(actual_loss as decimal(18, 2))                          as actual_loss,
        try_cast(cumulative_modification_costs as decimal(18, 2))        as cumulative_modification_costs,
        try_cast(current_period_modification_costs as decimal(18, 2))    as current_period_modification_costs,
        try_cast(estimated_loan_to_value_eltv as decimal(6, 2))          as estimated_ltv,
        payment_deferral_flag,
        delinquency_due_to_disaster,
        borrower_assistance_plan,
        servicer_name,
        source_file,
        loaded_at

    from source

)

select * from renamed
