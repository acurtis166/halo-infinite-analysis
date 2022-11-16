/**/

CREATE OR REPLACE VIEW vw_match AS

SELECT
    m.id,
    m.match_id,
    m.start_time,
    m.end_time,
    m.duration,
    m.playable_duration,
    lc.name AS lifecycle_mode,
    gvc.name AS game_variant_category,
    -- level?
    mv.name AS map_variant,
    gv.name AS game_variant,
    pl.name AS playlist,
    plex.name AS playlist_experience,
    mmp.name AS map_mode_pair
FROM match m
JOIN lifecycle_mode lc ON m.lifecycle_mode_id = lc.id
JOIN game_variant_category gvc ON m.game_variant_category_id = gvc.id
JOIN map_variant mv ON m.map_variant_id = mv.id
JOIN game_variant gv ON m.game_variant_id = gv.id
JOIN playlist pl ON m.playlist_id = pl.id
JOIN playlist_experience plex ON m.playlist_experience_id = plex.id
JOIN playlist_map_mode_pair mmp ON m.playlist_map_mode_pair_id = mmp.id