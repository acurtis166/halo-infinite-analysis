CREATE TABLE IF NOT EXISTS team_stat (
    id serial PRIMARY KEY,
    match_id int REFERENCES match (id) NOT NULL,
    team_id smallint NOT NULL,
    outcome_id smallint REFERENCES outcome (id),
    rank smallint,
    score smallint,
    personal_score integer,
    rounds_won smallint,
    rounds_lost smallint,
    rounds_tied smallint,
    kills smallint,
    deaths smallint,
    assists smallint,
    suicides smallint,
    betrayals smallint,
    grenade_kills smallint,
    headshot_kills smallint,
    melee_kills smallint,
    power_weapon_kills smallint,
    shots_fired smallint,
    shots_hit smallint,
    damage_dealt integer,
    damage_taken integer,
    callout_assists smallint,
    driver_assists smallint,
    emp_assists smallint,
    vehicle_destroys smallint,
    hijacks smallint,
    max_killing_spree smallint
);

CREATE UNIQUE INDEX team_stat_idx_match_team ON team_stat (match_id, team_id);