CREATE TABLE IF NOT EXISTS match (
    id serial PRIMARY KEY,
    match_id uuid UNIQUE NOT NULL,
    start_time timestamptz,
    end_time timestamptz,
    duration real,
    lifecycle_mode_id smallint REFERENCES lifecycle_mode (id),
    game_variant_category_id smallint REFERENCES game_variant_category (id),
    level_id smallint REFERENCES level (id),
    map_variant_id smallint REFERENCES map_variant (id),
    game_variant_id smallint REFERENCES game_variant (id),
    playlist_id smallint REFERENCES playlist (id),
    playlist_experience_id smallint REFERENCES playlist_experience (id),
    playlist_map_mode_pair_id smallint REFERENCES playlist_map_mode_pair (id),
    playable_duration real
);