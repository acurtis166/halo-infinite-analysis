
import argparse
import collections
import datetime as dt
import functools
import io
import json
import multiprocessing as mp
import multiprocessing.pool
import pathlib
import time
from typing import Callable, Set
import uuid

import psycopg2.extensions
import requests
from spnkr.api.authorities.stats.models import MatchStats, PlayerMatchHistoryRecord
from spnkr.api.authorities.skill.models import MatchSkillInfo
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


def do_work(conn: psycopg2.extensions.connection,
            pool: multiprocessing.pool.Pool,
            schema: str,
            player_batch_size: int,
            match_batch_size: int,
            player_func: Callable[[int], list[PlayerMatchHistoryRecord]],
            stats_func: Callable[[uuid.UUID], MatchStats | None],
            skill_func: Callable[[uuid.UUID, list[str]], tuple[uuid.UUID, list[MatchSkillInfo]] | None]
            ) -> bool:
    p_queue = db.get_player_queue_needing_history(conn, schema, player_batch_size)
    print(f'{len(p_queue)} players')
    if p_queue:
        match_ids: set[uuid.UUID] = set()
        for pres in pool.map(player_func, p_queue):
            match_ids = match_ids.union(m.match_id for m in pres)
        db.create_match_queues(conn, schema, [(mid,) for mid in match_ids])
        db.update_player_queue_history(conn, schema, p_queue)

    m_queue = db.get_match_queues(conn, schema, match_batch_size)
    print(f'{len(m_queue)} matches')
    if not m_queue:
        return False

    match_io = io.StringIO()
    team_io = io.StringIO()
    player_io = io.StringIO()
    xuids: Set[int] = set()
    match_xuids: dict[uuid.UUID, list[str]] = collections.defaultdict(list)
    for mstats in pool.map(stats_func, m_queue):
        if mstats is None:
            continue
        match_io.write(f'{api.create_match_tab_sep_vals(mstats)}')
        for xuid in api.iter_player_xuids(mstats):
            xuids.add(int(util.unwrap_xuid(xuid)))
            match_xuids[mstats.match_id].append(xuid)
        for trecord in api.iter_team_stats_tab_sep_vals(mstats):
            team_io.write(f'{trecord}')
        for precord in api.iter_player_stats_tab_sep_vals(mstats):
            player_io.write(f'{precord}')

    skill_io = io.StringIO()
    for tup in pool.starmap(skill_func, list(match_xuids.items())):
        if tup is None:
            continue
        match_id, mskills = tup
        for mskill in mskills:
            for skill_record in api.iter_skill_tab_sep_vals(mskill, match_id):
                skill_io.write(f'{skill_record}')

    db.create_player_queues(conn, schema, [(x,) for x in xuids])
    db.create_matches(conn, schema, match_io)
    db.create_team_stats(conn, schema, team_io)
    db.create_player_stats(conn, schema, player_io)
    db.create_skill(conn, schema, skill_io)
    db.update_match_queue(conn, schema, m_queue)

    return True


def main(schema: str,
         duration: int,
         workers: int,
         player_batch_size: int,
         match_batch_size: int,
         start_date: dt.datetime,
         end_date: dt.datetime):
    oauth_token = OAuth2TokenResponse.parse_json((ROOT / 'oauth_token.json').read_text())

    with db.connect(**CONFIG['database']) as conn, requests.session() as sess, mp.Pool(workers) as pool:
        auth_mgr = AuthenticationManager(sess, AZURE_APP['id'], AZURE_APP['secret'],
                                         AZURE_APP['redirect_uri'])
        auth_mgr.oauth = oauth_token
        client = Client(auth_mgr)
        player_func = functools.partial(api.get_matches, client, start_date=start_date, end_date=end_date)
        stats_func = functools.partial(api.get_match_stats, client)
        skill_func = functools.partial(api.get_skills, client)
        start_time = time.time()
        while (time.time() - start_time) < duration:
            if not do_work(conn, pool, schema, player_batch_size, match_batch_size, player_func, stats_func, skill_func):
                break


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--schema', '-s', type=str, required=True)
    argparser.add_argument('--duration', '-d', type=int, default=60)
    argparser.add_argument('--workers', '-w', type=int, default=4)
    argparser.add_argument('--player_batch_size', '-pb', type=int, default=4)
    argparser.add_argument('--match_batch_size', '-mb', type=int, default=100)
    args = argparser.parse_args()

    # logging.basicConfig(filename='run.log', filemode='w', level=logging.ERROR)

    start = dt.datetime(2022, 11, 1, tzinfo=dt.timezone.utc)
    end = start + dt.timedelta(days=7)

    main(args.schema, args.duration, args.workers, args.player_batch_size, args.match_batch_size, start, end)

