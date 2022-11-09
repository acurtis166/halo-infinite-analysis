

import argparse
import json
import pathlib

from halo_infinite_analysis import db


ROOT = pathlib.Path(__file__).parents[1]
CONFIG = json.loads((ROOT / 'config.json').read_text())


def main(schema: str, seed_xuid: int):
    with db.connect(**CONFIG['database']) as conn:
        db.create_schema(conn, schema)
        db.create_tables(conn, schema)
        db.create_player_queues(conn, schema, [(seed_xuid,)])


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--schema', '-s', type=str, required=True)
    args = argparser.parse_args()

    acurtis = 2535445291321133
    main(args.schema, acurtis)

