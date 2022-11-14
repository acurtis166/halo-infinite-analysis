CREATE TABLE IF NOT EXISTS game_variant (
    id smallserial PRIMARY KEY,
    asset_id uuid NOT NULL,
    version_id uuid NOT NULL,
    name text
);

CREATE UNIQUE INDEX game_variant_idx_asset_version ON game_variant (asset_id, version_id);