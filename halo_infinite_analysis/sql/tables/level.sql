CREATE TABLE IF NOT EXISTS level (
    id smallserial PRIMARY KEY,
    level_id uuid UNIQUE NOT NULL
);