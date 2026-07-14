with int_crew as (
    select * from {{ ref('int_crew') }}
)
select 
    {{ dbt_utils.generate_surrogate_key(['movie_id', 'crew_member_id']) }} as movie_crew_sk,
    *
from int_crew