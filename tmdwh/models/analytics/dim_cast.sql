with int_cast as (
    select * from {{ ref('int_cast') }}
)
select 
    {{ dbt_utils.generate_surrogate_key(['movie_id', 'cast_id']) }} as movie_actor_sk,
    *
from int_cast