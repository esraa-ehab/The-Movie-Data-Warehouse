with staging_cast as (

    select 
        movie_id,
        raw_cast
    from {{ ref('stg_cast') }}

),

flattened_cast as (

    select
        m.movie_id,
        c.id as cast_id,
        c.name as cast_name,
        c.gender as cast_gender,
        c.credit_id as cast_credit_id,
        c.popularity as cast_popularity,
        c.known_for_department as cast_department,
        c."order" as cast_order 
        
    from staging_cast m
    cross join lateral jsonb_to_recordset(m.raw_cast) as c(
        id integer, 
        name varchar, 
        gender integer, 
        credit_id varchar, 
        popularity float, 
        known_for_department varchar,
        "order" integer 
    )
    where c."order" <= 5 

)

select * from flattened_cast