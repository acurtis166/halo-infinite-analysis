CREATE TABLE IF NOT EXISTS map_variant (
    id smallserial PRIMARY KEY,
    asset_id uuid NOT NULL,
    version_id uuid NOT NULL,
    name text
);

CREATE UNIQUE INDEX IF NOT EXISTS map_variant_idx_asset_version ON map_variant (asset_id, version_id);