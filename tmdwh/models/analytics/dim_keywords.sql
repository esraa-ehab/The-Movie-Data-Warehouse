with int_keywords as (
    select * from {{ ref('int_keywords') }}
)
select 
    {{ dbt_utils.generate_surrogate_key(['movie_id', 'keyword_id']) }} as movie_keyword_sk,
    *
from int_keywords