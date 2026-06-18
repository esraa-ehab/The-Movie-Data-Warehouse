with staging_spoken_languages as (

    select 
        movie_id,
        raw_spoken_languages
    from {{ ref('stg_spoken_languages') }}

),

flattened_spoken_languages as (

    select
        m.movie_id,
        c.iso_639_1 as language_iso_code,
        c.name as language_name,
        c.english_name as language_english_name
    from staging_spoken_languages m
    cross join lateral jsonb_to_recordset(m.raw_spoken_languages) as c(iso_639_1 varchar, name varchar, english_name varchar)

)

select * from flattened_spoken_languages