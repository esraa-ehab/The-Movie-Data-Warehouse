with int_production_companies as (
    select * from {{ ref('int_production_companies') }}
)
select 
    *
from int_production_companies