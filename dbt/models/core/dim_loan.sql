with originations as (

    select * from {{ ref('stg_originations') }}

),

-- Defensive de-dup: keep the most recently loaded record per loan in case a
-- future incremental load lands a corrected record for the same loan_identifier.
deduped as (

    select
        *,
        row_number() over (
            partition by loan_identifier
            order by loaded_at desc
        ) as row_num

    from originations

)

select
    loan_identifier,
    pre_harp_loan_sequence_number,
    credit_score,
    vantage_score_4_0,
    first_payment_date,
    maturity_date,
    year(first_payment_date)                                              as vintage_year,
    quarter(first_payment_date)                                           as vintage_quarter,
    concat('Q', quarter(first_payment_date), ' ', year(first_payment_date)) as vintage_label,
    first_time_homebuyer_indicator,
    msa_code,
    mi_percentage,
    number_of_units,
    occupancy_status,
    original_cltv,
    original_dti,
    original_upb,
    original_ltv,
    original_interest_rate,
    channel,
    prepayment_penalty_indicator,
    amortization_type,
    property_state,
    property_type,
    postal_code,
    loan_purpose,
    original_loan_term_months,
    number_of_borrowers,
    seller_name,
    super_conforming_flag,
    special_eligibility_program,
    harp_indicator,
    property_valuation_method,
    interest_only_i_o_indicator
from deduped
where row_num = 1
