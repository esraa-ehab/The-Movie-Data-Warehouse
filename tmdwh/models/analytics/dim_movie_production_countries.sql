with int_production_countries as (
    select * from {{ ref('int_production_countries') }}
)
select 
    *
from int_production_countries