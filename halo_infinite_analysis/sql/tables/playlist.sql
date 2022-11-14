CREATE TABLE IF NOT EXISTS playlist (
    id smallserial PRIMARY KEY,
    asset_id uuid NOT NULL,
    version_id uuid NOT NULL,
    name text
);

CREATE UNIQUE INDEX playlist_idx_asset_version ON playlist (asset_id, version_id);