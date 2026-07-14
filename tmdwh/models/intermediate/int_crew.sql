with staging_crew as (

    select 
        movie_id,
        raw_crew
    from {{ ref('stg_crew') }}

),

flattened_crew as (

    select
        m.movie_id,
        c.id as crew_member_id,
        c.name as crew_name,
        c.job as crew_job,
        c.gender as crew_gender,
        c.credit_id as crew_credit_id,
        c.popularity as crew_popularity,
        c.department as crew_department,
        c.known_for_department as crew_known_for_department
    from staging_crew m
    cross join lateral jsonb_to_recordset(m.raw_crew) as c(
        id integer, 
        name varchar, 
        job varchar, 
        gender integer, 
        credit_id varchar, 
        popularity float, 
        department varchar, 
        known_for_department varchar
    )
    where c.job in ({{ "'" ~ var('crew_included_jobs') | join("', '") ~ "'" }})

)

select * from flattened_crew