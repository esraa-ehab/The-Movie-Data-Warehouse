with source_data as (

    select * from {{ source('raw_api', 'raw_movies') }}

),

stg_spoken_languages as (

    select
        cast(movie_data ->> 'id' as integer) as movie_id,
        (movie_data -> 'spoken_languages') as raw_spoken_languages

    from source_data

)

select * from stg_spoken_languages