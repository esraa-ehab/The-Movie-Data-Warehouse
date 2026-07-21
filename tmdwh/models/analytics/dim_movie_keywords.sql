with int_keywords as (
    select * from {{ ref('int_keywords') }}
)
select 
    *
from int_keywords