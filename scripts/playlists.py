
import json
import pathlib

import psycopg2.extensions
import requests
from spnkr.api.authorities.stats.models import MatchStats, PlayerMatchHistoryRecord
from spnkr.api.authorities.skill.models import MatchSkillInfo
from spnkr.api.client import Client
from spnkr.api.enums import MatchType
from spnkr.authentication.manager import AuthenticationManager
from spnkr.authentication.models import OAuth2TokenResponse
from spnkr import util


ROOT = pathlib.Path(__file__).parents[1]
CONFIG = json.loads((ROOT / 'config.json').read_text())
AZURE_APP = json.loads(pathlib.Path('client.json').read_text())  # TODO move to config


def main():
    oauth_token = OAuth2TokenResponse.parse_json((ROOT / 'oauth_token.json').read_text())

    playlists = [
        ('dc4929de-216c-43bc-b207-1702253f4576', '32ec515a-7f93-45b9-9fe1-4d3fb55d1f8d'),
        ('7de5ed5b-381e-49e5-b334-d959056dbc2b', 'd0db0837-5ff7-4e84-b269-a7f49797d419'),
        ('325c18a5-d85b-4ba6-b98f-21465d9c19e2', '944ef899-1357-409b-ac64-6e2e6b143242'),
        ('f336c231-e55c-46c9-af11-d9acf1b3245d', '7f737fa7-d2aa-41ca-80d9-f8a09a09420f'),
        ('73b48e1e-05c4-4004-927d-965549b28396', '84d68884-50dd-47b4-b597-3a593b33a1a5'),
        ('70bb9184-e674-4307-8846-239ab4a30cb6', '51b5a382-2039-4392-a19b-c8f396910299'),
        ('7d9828c7-8184-4421-ad14-824fce8f7ebe', 'ab74d11c-f681-4224-bd8f-56d91a49b229'),
        ('4829f027-a9af-4b2f-86dd-7b290d6bb0a4', 'cc95c4c7-3721-461c-a533-de1f7b82c906'),
        ('71734db4-4b8e-4682-9206-62b6eff92582', 'b161f3d3-5e75-43c1-85e1-4a981fe90e1d'),
        ('bdceefb3-1c52-4848-a6b7-d49acd13109d', 'c9a74445-4518-4622-88fb-3d5c8c138c29'),
        ('f7f30787-f607-436b-bdec-44c65bc2ecef', 'bbd2a618-71be-4167-ae8b-f4b3ce20e0f9'),
        ('fa5aa2a3-2428-4912-a023-e1eeea7b877c', '0bac0a97-59b9-4a15-b472-99b1e01e3c70'),
        ('edfef3ac-9cbe-4fa2-b949-8f29deafd483', '6c1bb887-628f-4a16-a794-f07adad39a38'),
        ('aa41f6a9-51be-4f25-a53f-48192ce14de7', 'b63e0017-1821-4032-b24c-b76eb6bf1b3c'),
        ('3facc347-6e49-40c9-b9e7-503d26092eed', 'c18a81c8-d989-49a9-960c-3ea5fb490123'),
    ]
		
    with requests.session() as sess:
        auth_mgr = AuthenticationManager(sess, AZURE_APP['id'], AZURE_APP['secret'],
                                         AZURE_APP['redirect_uri'])
        auth_mgr.oauth = oauth_token
        client = Client(auth_mgr)

        for a, v in playlists:
            p = client.ugc_discovery.get_playlist(a, v)
            print(p.public_name)
    

if __name__ == '__main__':
    main()

