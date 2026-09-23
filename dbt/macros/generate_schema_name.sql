{% macro generate_schema_name(custom_schema_name, node) -%}
    {#- Use the custom schema exactly as given (e.g. "core") instead of dbt's
       default "<target_schema>_<custom_schema>" prefixing behavior. -#}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
