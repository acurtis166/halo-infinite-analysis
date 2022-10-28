
import argparse
import collections
import datetime as dt
import io
import json
import pathlib
from typing import Set
import uuid

import requests
from spnkr.api.client import Client
from spnkr.api.enums import MatchType
from spnkr.authentication.manager import AuthenticationManager
from spnkr.authentication.models import OAuth2TokenResponse
from spnkr import util

from halo_infinite_analysis import db
from halo_infinite_analysis import api


ROOT = pathlib.Path(__file__).parents[1]
CONFIG = json.loads((ROOT / 'config.json').read_text())
AZURE_APP = json.loads(pathlib.Path('client.json').read_text())  # TODO move to config


def main(schema: str):
    acurtis = '2535445291321133'
    start = dt.datetime(2022, 10, 20, 12, 0, 0, tzinfo=dt.timezone.utc)
    end = start + dt.timedelta(days=7)

    oauth_token = OAuth2TokenResponse.parse_json((ROOT / 'oauth_token.json').read_text())

    with db.connect(**CONFIG['database']) as conn:
        db_match_ids = db.get_match_queues(conn, schema)

    with requests.session() as sess:
        auth_mgr = AuthenticationManager(sess, AZURE_APP['id'], AZURE_APP['secret'],
                                         AZURE_APP['redirect_uri'])
        auth_mgr.oauth = oauth_token
        client = Client(auth_mgr)

        # match_ids = [(m.match_id,) for m in stats.iter_matches(client, acurtis, start, end)]
        # db.create_matches(conn, schema, match_ids)
        
        match_io = io.StringIO()
        team_io = io.StringIO()
        player_io = io.StringIO()
        xuids: Set[int] = set()
        match_xuids: dict[uuid.UUID, list[str]] = collections.defaultdict(list)
        for mstats in api.iter_match_stats(client, db_match_ids[1:5]):
            match_io.write(f'{api.create_match_tab_sep_vals(mstats)}\n')
            for xuid in api.iter_player_xuids(mstats):
                xuids.add(int(util.unwrap_xuid(xuid)))
                match_xuids[mstats.match_id].append(xuid)
            for trecord in api.iter_team_stats_tab_sep_vals(mstats):
                team_io.write(f'{trecord}\n')
            for precord in api.iter_player_stats_tab_sep_vals(mstats):
                player_io.write(f'{precord}\n')

        skill_io = io.StringIO()
        for match_id, mskill in api.iter_skills(client, match_xuids):
            for skill_record in api.iter_skill_tab_sep_vals(mskill, match_id):
                skill_io.write(f'{skill_record}\n')

        with db.connect(**CONFIG['database']) as conn:
            db.create_player_queues(conn, schema, [(x,) for x in xuids])
            db.create_matches(conn, schema, match_io)
            db.create_team_stats(conn, schema, team_io)
            db.create_player_stats(conn, schema, player_io)
            db.create_skill(conn, schema, skill_io)
            db.update_match_queue(conn, schema, db_match_ids)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--schema', '-s', type=str, required=True)
    args = argparser.parse_args()

    main(args.schema)

