{% macro delinquency_bucket(delinquency_months_col, zero_balance_code_col) -%}
    {#- Shared delinquency-bucket definition (charter section 10 metric dictionary),
       so staging and mart models classify loan status the same way everywhere. -#}
    case
        when {{ zero_balance_code_col }} is not null and {{ zero_balance_code_col }} != '' then 'Closed'
        when {{ delinquency_months_col }} = 0 then 'Current'
        when {{ delinquency_months_col }} = 1 then '30-59 DPD'
        when {{ delinquency_months_col }} = 2 then '60-89 DPD'
        when {{ delinquency_months_col }} >= 3 then '90+ DPD'
        else 'Unknown'
    end
{%- endmacro %}
