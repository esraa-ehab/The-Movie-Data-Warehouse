with source_data as (

    select * from {{ source('raw_api', 'raw_movies') }}

),

stg_genres as (

    select
        cast(movie_data ->> 'id' as integer) as movie_id,
        (movie_data -> 'genres') as raw_genres

    from source_data

)

select * from stg_genres