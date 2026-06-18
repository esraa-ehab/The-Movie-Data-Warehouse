with source_data as (

    select * from {{ source('raw_api', 'raw_movies') }}

),

stg_production_companies as (

    select
        cast(movie_data ->> 'id' as integer) as movie_id,
        (movie_data -> 'production_companies') as raw_production_companies,
        (movie_data -> 'production_countries') as raw_production_countries

    from source_data

)
select * from stg_production_companies