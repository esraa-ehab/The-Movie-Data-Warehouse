with source_data as (

    select * from {{ source('raw_api', 'raw_movies') }}

),

stg_cast as (

    select
        cast(movie_data ->> 'id' as integer) as movie_id,
        (movie_data -> 'credits' -> 'cast') as raw_cast

    from source_data

)

select * from stg_cast