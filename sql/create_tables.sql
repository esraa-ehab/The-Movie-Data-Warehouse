drop table if exists staging.staging_movie_ids;
create table staging.staging_movie_ids (
    tmdb_id INT primary key,
    original_title TEXT,
    popularity NUMERIC,
    extraction_status TEXT DEFAULT 'skipped', --(Skiped, Pending, Completed, Failed)
    last_updated_at DATE DEFAULT CURRENT_TIMESTAMP
);

drop table if exists staging.raw_movies;
CREATE TABLE staging.raw_movies (
    tmdb_id INT PRIMARY KEY,
    movie_data JSONB,         -- Stores the full JSON response
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);