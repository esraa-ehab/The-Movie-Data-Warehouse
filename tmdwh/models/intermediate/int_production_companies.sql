with staging_production as (

    select 
        movie_id,
        raw_production_companies
    from {{ ref('stg_production_companies') }}

),

unnested_companies as (

    select
        m.movie_id,
        com.id as production_company_id,
        com.name as production_company_name,
        com.origin_country as production_company_origin_country
    from staging_production m
    left join lateral jsonb_to_recordset(m.raw_production_companies) 
        as com(id integer, name varchar, origin_country varchar)
        on true

)

select * from unnested_companies