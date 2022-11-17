CREATE TABLE IF NOT EXISTS lifecycle_mode (
    id smallint PRIMARY KEY,
    name text
);

INSERT INTO lifecycle_mode
VALUES
    (1, 'Custom'),
    (3, 'Matchmade')
ON CONFLICT DO NOTHING;