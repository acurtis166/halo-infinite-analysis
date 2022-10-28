
CREATE TABLE IF NOT EXISTS match_queue (
    id uuid PRIMARY KEY,
    is_completed boolean DEFAULT false,
    rand smallint DEFAULT round(random() * 10000)
);

CREATE INDEX IF NOT EXISTS match_queue_idx_rand ON match_queue (rand);