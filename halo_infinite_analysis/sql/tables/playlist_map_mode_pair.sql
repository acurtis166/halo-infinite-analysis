CREATE TABLE IF NOT EXISTS playlist_map_mode_pair (
    id smallserial PRIMARY KEY,
    asset_id uuid NOT NULL,
    version_id uuid NOT NULL,
    name text
);

CREATE UNIQUE INDEX playlist_map_mode_idx_asset_version ON playlist_map_mode_pair (asset_id, version_id);