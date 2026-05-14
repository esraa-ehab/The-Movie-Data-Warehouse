drop table if exists raw.staging_movie_ids;
create table raw.staging_movie_ids (
    tmdb_id INT primary key,
    original_title TEXT,
    popularity NUMERIC,
    extraction_status TEXT DEFAULT 'skipped', --(Skiped, Pending, Completed, Failed)
    last_updated_at DATE DEFAULT CURRENT_TIMESTAMP
);

drop table if exists raw.raw_movies;
CREATE TABLE raw.raw_movies (
    tmdb_id INT PRIMARY KEY,
    movie_data JSONB,         -- Stores the full JSON response
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

drop table if exists raw.pipeline_metadata;
CREATE TABLE raw.pipeline_metadata (
    pipeline_name TEXT PRIMARY KEY,
    last_run_timestamp TIMESTAMP,
    status TEXT
);