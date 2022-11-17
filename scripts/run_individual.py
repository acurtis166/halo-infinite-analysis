
import argparse
import datetime as dt
import io
import json
import logging
import pathlib

import psycopg2.extensions
import requests
from spnkr.api.client import Client
from spnkr.authentication.manager import AuthenticationManager
from spnkr.authentication.models import OAuth2TokenResponse

from halo_infinite_analysis import db
from halo_infinite_analysis import api


ROOT = pathlib.Path(__file__).parents[1]
CONFIG = json.loads((ROOT / 'config.json').read_text())
AZURE_APP = json.loads(pathlib.Path('client.json').read_text())  # TODO move to config


def do_work(conn: psycopg2.extensions.connection,
            schema: str,
            client: Client,
            xuid: int,
            start_date: dt.datetime,
            end_date: dt.datetime):
    print(f'Collecting matches on or after {start_date}')
    match_ids = [m.match_id for m in api.get_matches(client, xuid, start_date, end_date)]
    print(f'{len(match_ids)} new matches')

    print('Collecting stats')
    match_io = io.StringIO()
    team_io = io.StringIO()
    player_io = io.StringIO()
    for mstats in (api.get_match_stats(client, mid) for mid in match_ids):
        if mstats is None:
            continue
        match_io.write(f'{api.create_match_tab_sep_vals(mstats)}')
        for trecord in api.iter_team_stats_tab_sep_vals(mstats):
            team_io.write(f'{trecord}')
        for precord in api.iter_player_stats_tab_sep_vals(mstats):
            player_io.write(f'{precord}')

    print('Collecting skills')
    skill_io = io.StringIO()
    for tup in (api.get_skills(client, mid, [str(xuid)]) for mid in match_ids):
        if tup is None:
            continue
        match_id, mskills = tup
        for mskill in mskills:
            for skill_record in api.iter_skill_tab_sep_vals(mskill, match_id):
                skill_io.write(f'{skill_record}')

    print('Inserting records into DB')
    db.create_matches(conn, schema, match_io)
    db.create_team_stats(conn, schema, team_io)
    db.create_player_stats(conn, schema, player_io)
    db.create_skill(conn, schema, skill_io)


def main(schema: str, xuid: int):
    oauth_token = OAuth2TokenResponse.parse_json((ROOT / 'oauth_token.json').read_text())

    with db.connect(**CONFIG['database']) as conn, requests.session() as sess:
        auth_mgr = AuthenticationManager(sess, AZURE_APP['id'], AZURE_APP['secret'],
                                         AZURE_APP['redirect_uri'])
        auth_mgr.oauth = oauth_token
        client = Client(auth_mgr)
        start_date = (db.get_latest_match_date(conn, schema)
                      or dt.datetime(1900, 1, 1, tzinfo=dt.timezone.utc))
        end_date = dt.datetime(2999, 1, 1, tzinfo=dt.timezone.utc)
        do_work(conn, schema, client, xuid, start_date, end_date)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--schema', '-s', type=str, required=True)
    argparser.add_argument('--xuid', '-x', type=int, default=2535445291321133)  # aCurtis X89
    args = argparser.parse_args()

    logging.basicConfig(filename='run_individual.log', filemode='w', level=logging.ERROR)

    main(args.schema, args.xuid)

