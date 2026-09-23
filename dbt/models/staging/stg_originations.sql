with source as (

    select * from {{ source('bronze', 'originations_raw') }}

),

renamed as (

    select
        loan_identifier,
        pre_harp_loan_sequence_number,
        try_cast(classic_fico as int)                                     as credit_score,
        try_cast(vantagescore_4_0 as int)                                 as vantage_score_4_0,
        to_date(first_payment_date || '01', 'yyyyMMdd')                   as first_payment_date,
        to_date(maturity_date || '01', 'yyyyMMdd')                        as maturity_date,
        first_time_homebuyer_indicator,
        metropolitan_statistical_area_msa_or_metropolitan_division        as msa_code,
        try_cast(mortgage_insurance_percentage_mi as decimal(5, 2))       as mi_percentage,
        try_cast(number_of_units as int)                                  as number_of_units,
        occupancy_status,
        try_cast(original_combined_loan_to_value_cltv as decimal(6, 2))   as original_cltv,
        try_cast(original_debt_to_income_dti_ratio as decimal(6, 2))      as original_dti,
        try_cast(original_upb as decimal(18, 2))                         as original_upb,
        try_cast(original_loan_to_value_ltv as decimal(6, 2))             as original_ltv,
        try_cast(original_interest_rate as decimal(8, 3))                 as original_interest_rate,
        channel,
        prepayment_penalty_indicator,
        amortization_type,
        property_state,
        property_type,
        postal_code,
        loan_purpose,
        try_cast(original_loan_term as int)                               as original_loan_term_months,
        try_cast(number_of_borrowers as int)                              as number_of_borrowers,
        seller_name,
        super_conforming_flag,
        special_eligibility_program,
        harp_indicator,
        property_valuation_method,
        interest_only_i_o_indicator,
        source_file,
        loaded_at

    from source

)

select * from renamed
