CREATE TABLE IF NOT EXISTS team_skill (
    id serial PRIMARY KEY,
    match_id int REFERENCES match (id) NOT NULL,
    team_id smallint NOT NULL,
    result_code smallint,
    mmr real
);

CREATE UNIQUE INDEX team_skill_idx_match_team ON team_skill (match_id, team_id);