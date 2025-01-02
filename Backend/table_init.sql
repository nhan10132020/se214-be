-- Table: roles
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Table: users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    role_id INT REFERENCES roles(role_id),
    email VARCHAR(100) NOT NULL,
);

-- Table: genres
CREATE TABLE genres (
    genre_id bigint PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Table: movie_details
CREATE TABLE movie_details (
    movie_detail_id SERIAL PRIMARY KEY,
    homepage VARCHAR(255),
    budget BIGINT,
    tagline VARCHAR(255),
    revenue BIGINT,
    runtime INT,
    spoken_language text[],
    status VARCHAR(50),
    production_countries text[],
    production_companies text[],
    video_url VARCHAR(255),
);


-- Table: movies
CREATE TABLE movies (
    movie_id bigint PRIMARY KEY,
    adult BOOLEAN,
    origin_country VARCHAR(100),
    original_language VARCHAR(10),
    original_title VARCHAR(255),
    overview TEXT,
    popularity NUMERIC,
    backdrop_path VARCHAR(255),
    poster_path VARCHAR(255),
    release_date DATE,
    title VARCHAR(255) NOT NULL,
    vote_average NUMERIC,
    vote_count INT,
    movie_detail_id INT REFERENCES movie_details(movie_detail_id)
);

-- Table: actors
CREATE TABLE actors (
    actor_id bigint PRIMARY KEY,
    known_for_department VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    popularity NUMERIC,
    profile_path VARCHAR(255),
    gender VARCHAR(10)
);

-- Table: movie_has_actor
CREATE TABLE movie_has_actor (
    movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
    actor_id INT REFERENCES actors(actor_id) ON DELETE CASCADE,
    character VARCHAR(255),
    PRIMARY KEY (movie_id, actor_id)
);

-- Table: movie_has_genred
CREATE TABLE movie_has_genred (
    movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
    genre_id INT REFERENCES genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, actor_id)
);

-- Table: favourite_list
CREATE TABLE favourite_list (
    movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (movie_id, user_id)
);

-- Table: comments
CREATE TABLE comments (
    movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (movie_id, user_id)
);

-- Table: watch_histories
CREATE TABLE watch_histories (
    watch_history_id SERIAL PRIMARY KEY,
    movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);