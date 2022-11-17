CREATE TABLE IF NOT EXISTS playlist_experience (
    id smallint PRIMARY KEY,
    name text
);

INSERT INTO playlist_experience
VALUES
    (2, 'Arena'),
    (3, 'BigTeamBattle'),
    (4, 'PVE'),
    (5, 'Featured')
ON CONFLICT DO NOTHING;