CREATE TABLE IF NOT EXISTS player_skill (
    id serial PRIMARY KEY,
    match_id int REFERENCES match (id) NOT NULL,
    player_id int REFERENCES player (id) NOT NULL,
    team_id smallint NOT NULL,
    result_code smallint,
    pre_match_csr smallint,
    post_match_csr smallint,
    kills_expected real,
    deaths_expected real
);

CREATE UNIQUE INDEX player_skill_idx_match_player ON player_skill (match_id, player_id);