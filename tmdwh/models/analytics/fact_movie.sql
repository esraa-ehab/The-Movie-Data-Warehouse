with staging_data as (

    select 
        movie_id,
        release_date,
        runtime_minutes,
        vote_count,
        vote_average,
        popularity,
        budget,
        revenue
    from {{ ref('stg_movies') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['movie_id']) }} as movie_sk,
    movie_id,
    release_date,
    runtime_minutes,
    vote_count,
    vote_average,
    popularity,
    budget,
    revenue,
    case 
        when revenue is not null and budget is not null then (revenue - budget)
        else null 
    end as net_profit,
    case 
        when budget > 0 and revenue is not null then round(((revenue - budget)::numeric / budget::numeric), 4)
        else null 
    end as return_on_investment

from staging_data