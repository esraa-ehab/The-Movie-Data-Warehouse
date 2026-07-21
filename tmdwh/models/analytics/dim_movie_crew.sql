with int_crew as (
    select * from {{ ref('int_crew') }}
)
select 
    *
from int_crew