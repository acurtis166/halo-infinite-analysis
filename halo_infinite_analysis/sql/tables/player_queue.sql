
CREATE TABLE IF NOT EXISTS player_queue (
    xuid bigint PRIMARY KEY,
    history boolean DEFAULT false,
    rand smallint DEFAULT round(random() * 10000)
);

CREATE INDEX IF NOT EXISTS player_queue_idx_rand ON player_queue (rand);