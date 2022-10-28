CREATE TABLE IF NOT EXISTS skill (
    match_id uuid,
    xuid bigint,
    team_id smallint,
    result_code smallint,
    team_mmr real,
    pre_match_csr smallint,
    post_match_csr smallint,
    kills_expected real,
    deaths_expected real
)