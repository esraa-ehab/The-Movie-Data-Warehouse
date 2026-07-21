with int_languages as (
    select * from {{ ref('int_spoken_languages') }}
)
select 
    *
from int_languages