select
    loan_identifier,
    period_date,
    count(*) as record_count
from {{ ref('fact_loan_performance') }}
group by loan_identifier, period_date
having count(*) > 1
