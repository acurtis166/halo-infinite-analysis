CREATE TABLE IF NOT EXISTS match_dump (
    id uuid,
    start_time timestamptz,
    end_time timestamptz,
    duration real,
    lifecycle_mode smallint,
    game_variant_category smallint,
    level_id uuid,
    map_variant_asset_id uuid,
    map_variant_version_id uuid,
    game_variant_asset_id uuid,
    game_variant_version_id uuid,
    playlist_asset_id uuid,
    playlist_version_id uuid,
    playlist_experience smallint,
    playlist_map_mode_pair_asset_id uuid,
    playlist_map_mode_pair_version_id uuid,
    playable_duration real
)