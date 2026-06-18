with source_data as (

    select * from {{ source('raw_api', 'raw_movies') }}

),

stg_keywords as (

    select
        cast(movie_data ->> 'id' as integer) as movie_id,
        (movie_data -> 'keywords' -> 'keywords') as raw_keywords

    from source_data

)

select * from stg_keywords