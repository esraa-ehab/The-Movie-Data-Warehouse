with staging_data as (

    select 
        movie_id,
        title,
        original_title,
        overview,
        release_status,
        original_language,
        origin_country,
        is_adult,
        poster_path,
        backdrop_path
    from {{ ref('stg_movies') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['movie_id']) }} as movie_sk,
    *

from staging_data