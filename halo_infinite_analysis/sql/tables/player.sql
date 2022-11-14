CREATE TABLE IF NOT EXISTS player (
    id serial PRIMARY KEY,
    xuid bigint UNIQUE NOT NULL
);