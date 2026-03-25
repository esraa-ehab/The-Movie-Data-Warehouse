drop table if exists movies;
create table movies (
    movie_id INT primary key,
    title TEXT,
    release_date DATE,
    rating FLOAT,
    vote_count INT,
    language text,
    adult text,
    overview text
);

drop table if exists crew;
create table crew (
    crew_id SERIAL primary key,
    movie_id BIGINT references movies(movie_id),
    name TEXT not null,
    job TEXT,
    department TEXT
);