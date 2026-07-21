with int_genres as (
    select * from {{ ref('int_genres') }}
)
select 
    *
from int_genres