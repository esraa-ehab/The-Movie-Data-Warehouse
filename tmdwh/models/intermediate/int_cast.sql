with staging_cast as (

    select 
        movie_id,
        raw_cast
    from {{ ref('stg_cast') }}

),

flattened_cast as (

    select
        m.movie_id,
        c.id as actor_id,
        c.cast_id as cast_id,
        c.credit_id as cast_credit_id,
        c.name as cast_name,
        c."character" as character_played,
        c.gender as cast_gender, 
        c.popularity as cast_popularity,
        c.known_for_department as cast_department,
        c."order" as cast_order 
        
    from staging_cast m
    cross join lateral jsonb_to_recordset(m.raw_cast) as c(
        id integer, 
        cast_id integer,
        name varchar, 
        "character" varchar,
        gender integer, 
        credit_id varchar, 
        popularity float, 
        known_for_department varchar,
        "order" integer 
    )
    where c."order" <= {{ var('cast_top_n_order') }} 

)

select * from flattened_cast