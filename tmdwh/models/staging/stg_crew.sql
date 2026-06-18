with source_data as (

    select * from {{ source('raw_api', 'raw_movies') }}

),

stg_crew as (

    select
        cast(movie_data ->> 'id' as integer) as movie_id,
        (movie_data -> 'credits' -> 'crew') as raw_crew

    from source_data

)

select * from stg_crew