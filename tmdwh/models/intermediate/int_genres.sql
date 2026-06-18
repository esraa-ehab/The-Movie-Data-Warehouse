with staging_movies as (

    select 
        movie_id,
        raw_genres
    from {{ ref('stg_genres') }}

),

flattened_genres as (

    select
        m.movie_id,
        g.id as genre_id,
        g.name as genre_name
    from staging_movies m
    cross join lateral jsonb_to_recordset(m.raw_genres) as g(id integer, name varchar)

)

select * from flattened_genres