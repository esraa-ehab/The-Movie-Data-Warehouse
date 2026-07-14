with int_languages as (
    select * from {{ ref('int_spoken_languages') }}
)
select 
    {{ dbt_utils.generate_surrogate_key(['movie_id', 'language_iso_code']) }} as movie_language_sk,
    *
from int_languages