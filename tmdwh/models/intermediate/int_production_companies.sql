with staging_production as (

    select 
        movie_id,
        raw_production_companies,
        raw_production_countries
    from {{ ref('stg_production_companies') }}

),

unnested_companies as (

    select
        m.movie_id,
        com.id as production_company_id,
        com.name as production_company_name,
        com.origin_country as production_company_origin_country
    from staging_production m
    cross join lateral jsonb_to_recordset(m.raw_production_companies) 
        as com(id integer, name varchar, origin_country varchar)

),

unnested_countries as (

    select
        m.movie_id,
        coun.name as production_country_name,
        coun.iso_3166_1 as production_country_iso_code
    from staging_production m
    cross join lateral jsonb_to_recordset(m.raw_production_countries) 
        as coun(name varchar, iso_3166_1 varchar)

),

final as (

    select
        coalesce(c.movie_id, n.movie_id) as movie_id,
        c.production_company_id,
        c.production_company_name,
        c.production_company_origin_country,
        n.production_country_name,
        n.production_country_iso_code
    from unnested_companies c
    full outer join unnested_countries n 
        on c.movie_id = n.movie_id

)

select * from final