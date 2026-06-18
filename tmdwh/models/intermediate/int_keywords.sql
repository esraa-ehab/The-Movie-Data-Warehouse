with staging_keywords as (

    select 
        movie_id,
        raw_keywords
    from {{ ref('stg_keywords') }}

),

flattened_keywords as (

    select
        m.movie_id,
        k.id as keyword_id,
        k.name as keyword_name
        
    from staging_keywords m
    cross join lateral jsonb_to_recordset(m.raw_keywords) as k(id integer, name varchar)

)

select * from flattened_keywords