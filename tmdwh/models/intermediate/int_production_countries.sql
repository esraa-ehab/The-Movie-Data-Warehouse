with staging_production as (

    select 
        movie_id,
        raw_production_countries
    from {{ ref('stg_production_companies') }}

),

unnested_countries as (

    select
        m.movie_id,
        coun.name as production_country_name,
        coun.iso_3166_1 as production_country_iso_code
    from staging_production m
    left join lateral jsonb_to_recordset(m.raw_production_countries) 
        as coun(name varchar, iso_3166_1 varchar)
        on true

)

select * from unnested_countries