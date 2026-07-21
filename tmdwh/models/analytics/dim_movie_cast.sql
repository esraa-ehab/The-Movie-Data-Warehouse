with int_cast as (
    select * from {{ ref('int_cast') }}
)
select 
    *
from int_cast