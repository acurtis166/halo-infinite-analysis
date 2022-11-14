/**/

INSERT INTO level (level_id)
SELECT DISTINCT
    level_id
FROM match_dump
WHERE
    NOT EXISTS (SELECT 1 FROM level WHERE level_id = match_dump.level_id);


INSERT INTO map_variant (asset_id, version_id)
SELECT DISTINCT
    map_variant_asset_id,
    map_variant_version_id
FROM match_dump
WHERE
    NOT EXISTS (SELECT 1 FROM map_variant WHERE asset_id = match_dump.map_variant_asset_id AND version_id = match_dump.map_variant_version_id);


INSERT INTO game_variant (asset_id, version_id)
SELECT DISTINCT
    game_variant_asset_id,
    game_variant_version_id
FROM match_dump
WHERE
    NOT EXISTS (SELECT 1 FROM game_variant WHERE asset_id = match_dump.game_variant_asset_id AND version_id = match_dump.game_variant_version_id);


INSERT INTO playlist (asset_id, version_id)
SELECT DISTINCT
    playlist_asset_id,
    playlist_version_id
FROM match_dump
WHERE
    playlist_asset_id IS NOT NULL AND
    NOT EXISTS (SELECT 1 FROM playlist WHERE asset_id = match_dump.playlist_asset_id AND version_id = match_dump.playlist_version_id);


INSERT INTO playlist_map_mode_pair (asset_id, version_id)
SELECT DISTINCT
    playlist_map_mode_pair_asset_id,
    playlist_map_mode_pair_version_id
FROM match_dump
WHERE
    playlist_map_mode_pair_asset_id IS NOT NULL AND
    NOT EXISTS (SELECT 1 FROM playlist_map_mode_pair WHERE asset_id = match_dump.playlist_map_mode_pair_asset_id AND version_id = match_dump.playlist_map_mode_pair_version_id);


INSERT INTO lifecycle_mode
SELECT DISTINCT
    lifecycle_mode,
    '<unknown>'
FROM match_dump
WHERE
    NOT EXISTS (SELECT 1 FROM lifecycle_mode WHERE id = match_dump.lifecycle_mode);


INSERT INTO game_variant_category
SELECT DISTINCT
    game_variant_category,
    '<unknown>'
FROM match_dump
WHERE
    NOT EXISTS (SELECT 1 FROM game_variant_category WHERE id = match_dump.game_variant_category);


INSERT INTO playlist_experience
SELECT DISTINCT
    playlist_experience,
    '<unknown>'
FROM match_dump
WHERE
    NOT EXISTS (SELECT 1 FROM playlist_experience WHERE id = match_dump.playlist_experience);


INSERT INTO match (
    match_id,
    start_time,
    end_time,
    duration,
    lifecycle_mode_id,
    game_variant_category_id,
    level_id,
    map_variant_id,
    game_variant_id,
    playlist_id,
    playlist_experience_id,
    playlist_map_mode_pair_id,
    playable_duration
)
SELECT DISTINCT
    m.id,
    m.start_time,
    m.end_time,
    m.duration,
    m.lifecycle_mode,
    m.game_variant_category,
    lvl.id,
    mv.id,
    gv.id,
    p.id,
    m.playlist_experience,
    mmp.id,
    m.playable_duration
FROM match_dump m
LEFT JOIN level lvl ON m.level_id = lvl.level_id
LEFT JOIN map_variant mv ON m.map_variant_asset_id = mv.asset_id AND m.map_variant_version_id = mv.version_id
LEFT JOIN game_variant gv ON m.game_variant_asset_id = gv.asset_id AND m.game_variant_version_id = gv.version_id
LEFT JOIN playlist p ON m.playlist_asset_id = p.asset_id AND m.playlist_version_id = p.version_id
LEFT JOIN playlist_map_mode_pair mmp ON m.playlist_map_mode_pair_asset_id = mmp.asset_id AND m.playlist_map_mode_pair_version_id = mmp.version_id
WHERE
    NOT EXISTS (SELECT 1 FROM match WHERE match_id = m.id);


INSERT INTO player (xuid)
SELECT DISTINCT
    xuid
FROM player_dump
WHERE
    NOT EXISTS (SELECT 1 FROM player WHERE xuid = player_dump.xuid);


INSERT INTO player_stat (
    match_id,
    player_id,
    last_team_id,
    outcome_id,
    rank,
    first_joined_time,
    last_leave_time,
    present_at_beginning,
    joined_in_progress,
    left_in_progress,
    present_at_completion,
    time_played,
    confirmed_participation,
    team_id,
    score,
    personal_score,
    rounds_won,
    rounds_lost,
    rounds_tied,
    kills,
    deaths,
    assists,
    suicides,
    betrayals,
    grenade_kills,
    headshot_kills,
    melee_kills,
    power_weapon_kills,
    shots_fired,
    shots_hit,
    damage_dealt,
    damage_taken,
    callout_assists,
    driver_assists,
    emp_assists,
    vehicle_destroys,
    hijacks,
    max_killing_spree
)
SELECT DISTINCT
    m.id,
    p.id,
    pd.last_team_id,
    pd.outcome,
    pd.rank,
    pd.first_joined_time,
    pd.last_leave_time,
    pd.present_at_beginning,
    pd.joined_in_progress,
    pd.left_in_progress,
    pd.present_at_completion,
    pd.time_played,
    pd.confirmed_participation,
    pd.team_id,
    pd.score,
    pd.personal_score,
    pd.rounds_won,
    pd.rounds_lost,
    pd.rounds_tied,
    pd.kills,
    pd.deaths,
    pd.assists,
    pd.suicides,
    pd.betrayals,
    pd.grenade_kills,
    pd.headshot_kills,
    pd.melee_kills,
    pd.power_weapon_kills,
    pd.shots_fired,
    pd.shots_hit,
    pd.damage_dealt,
    pd.damage_taken,
    pd.callout_assists,
    pd.driver_assists,
    pd.emp_assists,
    pd.vehicle_destroys,
    pd.hijacks,
    pd.max_killing_spree
FROM player_dump pd
LEFT JOIN match m ON m.match_id = pd.match_id
LEFT JOIN player p ON p.xuid = pd.xuid
WHERE
    NOT EXISTS (SELECT 1 FROM player_stat WHERE match_id = m.id AND player_id = p.id AND team_id = pd.team_id);


INSERT INTO team_stat (
    match_id,
    team_id,
    outcome_id,
    rank,
    score,
    personal_score,
    rounds_won,
    rounds_lost,
    rounds_tied,
    kills,
    deaths,
    assists,
    suicides,
    betrayals,
    grenade_kills,
    headshot_kills,
    melee_kills,
    power_weapon_kills,
    shots_fired,
    shots_hit,
    damage_dealt,
    damage_taken,
    callout_assists,
    driver_assists,
    emp_assists,
    vehicle_destroys,
    hijacks,
    max_killing_spree
)
SELECT DISTINCT
    m.id,
    td.team_id,
    td.outcome,
    td.rank,
    td.score,
    td.personal_score,
    td.rounds_won,
    td.rounds_lost,
    td.rounds_tied,
    td.kills,
    td.deaths,
    td.assists,
    td.suicides,
    td.betrayals,
    td.grenade_kills,
    td.headshot_kills,
    td.melee_kills,
    td.power_weapon_kills,
    td.shots_fired,
    td.shots_hit,
    td.damage_dealt,
    td.damage_taken,
    td.callout_assists,
    td.driver_assists,
    td.emp_assists,
    td.vehicle_destroys,
    td.hijacks,
    td.max_killing_spree
FROM team_dump td
LEFT JOIN match m ON m.match_id = td.match_id
WHERE
    NOT EXISTS (SELECT 1 FROM team_stat WHERE match_id = m.id AND team_id = td.team_id);


INSERT INTO team_skill (
    match_id,
    team_id,
    result_code,
    mmr
)
SELECT DISTINCT
    m.id,
    sd.team_id,
    sd.result_code,
    sd.team_mmr
FROM skill_dump sd
LEFT JOIN match m ON sd.match_id = m.match_id
WHERE
    NOT EXISTS (SELECT 1 FROM team_skill WHERE match_id = m.id AND team_id = sd.team_id);


INSERT INTO player_skill (
    match_id,
    player_id,
    team_id,
    result_code,
    pre_match_csr,
    post_match_csr,
    kills_expected,
    deaths_expected
)
SELECT DISTINCT
    m.id,
    p.id,
    sd.team_id,
    sd.result_code,
    sd.pre_match_csr,
    sd.post_match_csr,
    sd.kills_expected,
    sd.deaths_expected
FROM skill_dump sd
LEFT JOIN match m ON sd.match_id = m.match_id
LEFT JOIN player p ON sd.xuid = p.xuid
WHERE
    NOT EXISTS (SELECT 1 FROM player_skill WHERE match_id = m.id AND player_id = p.id);