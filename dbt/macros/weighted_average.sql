{% macro weighted_average(value_col, weight_col) -%}
    {#- Null-safe weighted average: rows where value_col is null are excluded
       from both the numerator and the denominator, instead of silently
       treating them as zero-weighted. -#}
    sum(case when {{ value_col }} is not null then {{ weight_col }} * {{ value_col }} end)
        / nullif(sum(case when {{ value_col }} is not null then {{ weight_col }} end), 0)
{%- endmacro %}
