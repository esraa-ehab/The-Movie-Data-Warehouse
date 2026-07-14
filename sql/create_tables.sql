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

create table if not exists app.users (
    user_id GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS app.user_watchlists (
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    PRIMARY KEY (user_id, movie_id),
    
    CONSTRAINT fk_watchlist_user 
        FOREIGN KEY (user_id) 
        REFERENCES app.users (user_id) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_watchlist_movie 
        FOREIGN KEY (movie_id) 
        REFERENCES app.dim_movies_clean (movie_id) 
        ON DELETE CASCADE
);