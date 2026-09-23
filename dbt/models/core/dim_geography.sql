with originations as (

    select distinct
        property_state,
        msa_code,
        postal_code
    from {{ ref('stg_originations') }}
    where property_state is not null

)

select
    sha2(
        concat_ws('||', coalesce(property_state, ''), coalesce(msa_code, ''), coalesce(postal_code, '')),
        256
    ) as geography_key,
    property_state,
    msa_code,
    postal_code
from originations
