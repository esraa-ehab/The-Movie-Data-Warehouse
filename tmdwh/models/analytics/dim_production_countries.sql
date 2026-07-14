with int_production_countries as (
    select * from {{ ref('int_production_countries') }}
)
select 
    {{ dbt_utils.generate_surrogate_key(['movie_id', 'production_country_iso_code']) }} as movie_country_sk,
    *
from int_production_countries