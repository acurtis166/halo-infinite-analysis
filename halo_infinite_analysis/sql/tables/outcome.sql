CREATE TABLE IF NOT EXISTS outcome (
    id smallint PRIMARY KEY,
    name text
);

INSERT INTO outcome
VALUES
    (1, 'Tie'),
    (2, 'Win'),
    (3, 'Loss'),
    (4, 'DidNotFinish');