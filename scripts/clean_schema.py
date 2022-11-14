""""""

import argparse
import collections
import json
import pathlib
import uuid

import requests
from spnkr.api.client import Client
from spnkr.authentication.manager import AuthenticationManager
from spnkr.authentication.models import OAuth2TokenResponse

from halo_infinite_analysis import db


ROOT = pathlib.Path(__file__).parents[1]
CONFIG = json.loads((ROOT / 'config.json').read_text())
AZURE_APP = json.loads(pathlib.Path('client.json').read_text())  # TODO move to config


def main(schema: str):
    oauth_token = OAuth2TokenResponse.parse_json((ROOT / 'oauth_token.json').read_text())

    with db.connect(**CONFIG['database']) as conn, requests.session() as sess:
        auth_mgr = AuthenticationManager(sess, AZURE_APP['id'], AZURE_APP['secret'],
                                         AZURE_APP['redirect_uri'])
        auth_mgr.oauth = oauth_token
        client = Client(auth_mgr)

        print('Cleaning dumped data')
        db.clean_dumped_data(conn, schema)

        print('Removing data from staging tables')
        db.delete_dumped_data(conn, schema)

        print('Retrieving metadata information')
        db_client_funcs = (
            ('game_variant', db.get_game_variants, client.ugc_discovery.get_ugc_game_variant),
            ('map_variant', db.get_map_variants, client.ugc_discovery.get_map),
            ('playlist', db.get_playlists, client.ugc_discovery.get_playlist),
            ('playlist_map_mode_pair', db.get_playlist_map_mode_pairs, client.ugc_discovery.get_map_mode_pair),
        )
        tbl_records: dict[str, list[tuple[str, uuid.UUID, uuid.UUID]]] = collections.defaultdict(list)
        for tbl, db_func, c_func in db_client_funcs:
            for asset_id, version_id, name in db_func(conn, schema):
                if name is not None:
                    continue
                asset = c_func(str(asset_id), str(version_id))
                print(f'Retrieved {tbl} {asset.public_name}')
                tbl_records[tbl].append((asset.public_name, asset_id, version_id))

        for tbl, records in tbl_records.items():
            db.update_metadata(conn, schema, tbl, records)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--schema', '-s', type=str, required=True)
    args = argparser.parse_args()

    main(args.schema)

