CREATE TABLE IF NOT EXISTS game_variant_category (
    id smallint PRIMARY KEY,
    name text
);

INSERT INTO game_variant_category
VALUES
    (6, 'Slayer'),
    (7, 'Attrition'),
    (8, 'Elimination'),
    (9, 'Fiesta'),
    (11, 'Strongholds'),
    (12, 'Bastion'),
    (14, 'TotalControl'),
    (15, 'CTF'),
    (16, 'Assault'),
    (17, 'Extraction'),
    (18, 'Oddball'),
    (19, 'Stockpile'),
    (20, 'Juggernaut'),
    (23, 'Escort'),
    (24, 'GunGame'),
    (25, 'Grifball'),
    (32, 'TestEngine'),
    (39, 'LandGrab')
ON CONFLICT DO NOTHING;