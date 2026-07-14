with int_production_companies as (
    select * from {{ ref('int_production_companies') }}
)
select 
    {{ dbt_utils.generate_surrogate_key(['movie_id', 'production_company_id']) }} as movie_company_sk,
    *
from int_production_companies