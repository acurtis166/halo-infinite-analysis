CREATE TABLE IF NOT EXISTS player_stat (
    id serial PRIMARY KEY,
    match_id int REFERENCES match (id) NOT NULL,
    player_id int REFERENCES player (id) NOT NULL,
    last_team_id smallint,
    outcome_id smallint REFERENCES outcome (id),
    rank smallint,
    first_joined_time timestamptz,
    last_leave_time timestamptz,
    present_at_beginning boolean,
    joined_in_progress boolean,
    left_in_progress boolean,
    present_at_completion boolean,
    time_played real,
    confirmed_participation boolean,
    team_id smallint,
    score smallint,
    personal_score smallint,
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
    damage_dealt smallint,
    damage_taken smallint,
    callout_assists smallint,
    driver_assists smallint,
    emp_assists smallint,
    vehicle_destroys smallint,
    hijacks smallint,
    max_killing_spree smallint
);