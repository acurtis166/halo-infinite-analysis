
import json
import pathlib

import requests

from spnkr.api.client import Client
from spnkr.authentication.manager import AuthenticationManager
from spnkr.authentication.models import OAuth2TokenResponse


client_cfg = json.loads(pathlib.Path('client.json').read_text())
oauth_token = OAuth2TokenResponse.parse_json(pathlib.Path('oauth_token.json').read_text())


def main():
    with requests.session() as sess:
        auth_mgr = AuthenticationManager(sess, client_cfg['id'], client_cfg['secret'],
                                         client_cfg['redirect_uri'])
        auth_mgr.oauth = oauth_token
        client = Client(auth_mgr)

        match_count = client.stats.get_match_count('2535445291321133')

        print(match_count.to_json())


if __name__ == '__main__':
    main()

