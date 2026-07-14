{{ config(
    materialized='table',
    schema='app'
) }}

with clean_metadata as (
    select * from {{ ref('stg_movies') }}
),

raw_source as (
    select 
        cast(movie_data ->> 'id' as integer) as movie_id,
        movie_data
    from {{ source('raw_api', 'raw_movies') }}
)

select
    m.movie_id,
    m.title,
    m.original_title,
    m.overview,
    m.release_status,
    m.original_language,
    m.origin_country,
    m.is_adult,
    m.release_date,
    m.runtime_minutes,
    m.vote_count,
    m.vote_average,
    m.popularity,
    m.revenue,
    m.budget,

    coalesce(
        (select jsonb_agg(g->>'name') from jsonb_array_elements(r.movie_data->'genres') g),
        '[]'::jsonb
    ) as genres,

    coalesce(
        (select jsonb_agg(k->>'name') from jsonb_array_elements(r.movie_data->'keywords'->'keywords') k),
        '[]'::jsonb
    ) as keywords,

    coalesce(
        (select jsonb_agg(l->>'english_name') from jsonb_array_elements(r.movie_data->'spoken_languages') l),
        '[]'::jsonb
    ) as languages,

    coalesce(
        (select jsonb_agg(p->>'name') from jsonb_array_elements(r.movie_data->'production_companies') p),
        '[]'::jsonb
    ) as production_companies,

    coalesce(
        (
            select jsonb_agg(
                jsonb_build_object(
                    'actor_id', (cast_member->>'id')::int,
                    'cast_id', (cast_member->>'cast_id')::int,
                    'cast_credit_id', cast_member->>'credit_id',
                    'cast_name', cast_member->>'name',
                    'character_played', cast_member->>'character',
                    'cast_gender', (cast_member->>'gender')::int,
                    'cast_popularity', (cast_member->>'popularity')::numeric,
                    'cast_department', cast_member->>'known_for_department'
                )
                order by (cast_member->>'order')::int
            )
            from (
                select cast_member
                from jsonb_array_elements(r.movie_data->'credits'->'cast') as c(cast_member)
                order by (cast_member->>'order')::int
                limit 10
            ) top_cast_members
        ),
        '[]'::jsonb
    ) as top_cast,

    coalesce(
        (
            select jsonb_agg(
                jsonb_build_object(
                    'crew_id', (crew_member->>'id')::int,
                    'crew_credit_id', crew_member->>'credit_id',
                    'name', crew_member->>'name',
                    'job', crew_member->>'job',
                    'gender', (crew_member->>'gender')::int,
                    'popularity', (crew_member->>'popularity')::numeric,
                    'department', crew_member->>'department',
                    'known_for_department', crew_member->>'known_for_department'
                )
            )
            from jsonb_array_elements(r.movie_data->'credits'->'crew') as c(crew_member)
            where crew_member->>'job' in (
                'Director',
                'Producer',
                'Screenplay',
                'Writer',
                'Director of Photography',
                'Music'
            )
        ),
        '[]'::jsonb
    ) as top_crew
                    

from clean_metadata m
join raw_source r on m.movie_id = r.movie_id