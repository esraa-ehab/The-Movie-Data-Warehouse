with int_genres as (
    select * from {{ ref('int_genres') }}
)
select 
    {{ dbt_utils.generate_surrogate_key(['movie_id', 'genre_id']) }} as movie_genre_sk,
    *
from int_genres