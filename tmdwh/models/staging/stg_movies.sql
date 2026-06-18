with source_data as (

    select * from {{ source('raw_api', 'raw_movies') }}

),

stg_movies as (

    select 
        cast(movie_data ->> 'id' as integer) as movie_id,

        cast(movie_data ->> 'title' as varchar) as title,
        cast(movie_data ->> 'original_title' as varchar) as original_title,
        cast(movie_data ->> 'overview' as varchar) as overview,
        cast(movie_data ->> 'status' as varchar) as release_status,
        cast(movie_data ->> 'original_language' as varchar) as original_language,
        cast(movie_data ->> 'origin_country' as varchar) as origin_country,

        cast(movie_data ->> 'adult' as boolean) as is_adult,
        
        cast(movie_data ->> 'release_date' as date) as release_date,
    
        cast(movie_data ->> 'runtime' as integer) as runtime_minutes,
        cast(movie_data ->> 'vote_count' as integer) as vote_count,
        cast(movie_data ->> 'vote_average' as float) as vote_average,
        cast(movie_data ->> 'popularity' as float) as popularity,
        cast(movie_data ->> 'budget' as integer) as budget

    from source_data

)

select * from stg_movies