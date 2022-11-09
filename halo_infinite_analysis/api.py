
import datetime as dt
import logging
import math
from typing import Any
import uuid

import requests.exceptions
from spnkr.api.client import Client
from spnkr.api.authorities.stats.models import MatchStats, PlayerMatchHistoryRecord
from spnkr.api.authorities.skill.models import MatchSkillInfo
from spnkr.api.enums import MatchType, PlayerType
from spnkr import util


def get_matches(client: Client, xuid: int, start_date: dt.datetime, end_date: dt.datetime) -> list[PlayerMatchHistoryRecord]:
    out: list[PlayerMatchHistoryRecord] = []
    start = 0
    within_dates = False
    while True:
        try:
            match_history = client.stats.get_match_history(str(xuid), start,
                                                           match_type=MatchType.Matchmaking)
        except Exception as ex:
            logging.error(f'Error in stats.get_match_history(). {xuid=}, {start=}\n{ex}')
            start += 25
            continue
        for match in match_history.results:
            if not within_dates:
                if match.match_info.start_time > end_date:
                    continue
                within_dates = True
            if match.match_info.start_time < start_date:
                return out
            out.append(match)
        start += 25
        if match_history.result_count < 25:
            return out


def get_match_stats(client: Client, match_id: uuid.UUID):
    try:
        return client.stats.get_match_stats(str(match_id))
    except Exception as ex:
        logging.error(f'Error in stats.get_match_stats(). {match_id=}\n{ex}')


def get_skills(client: Client, match_id: uuid.UUID, xuids: list[str]):
    try:
        return (match_id, [client.skill.get_match_result(str(match_id), xuids)])
    except requests.exceptions.HTTPError as ex:
        if str(ex).startswith('400 Client Error: Invalid player ids'):
            idx = math.ceil(len(xuids) / 2)
            try:
                first_half = client.skill.get_match_result(str(match_id), xuids[:idx])
                second_half = client.skill.get_match_result(str(match_id), xuids[idx:])
                return (match_id, [first_half, second_half])
            except:
                logging.error(f'Error in skill.get_match_result(). {match_id=}, {xuids=}\n{ex}')
        logging.error(f'Error in skill.get_match_result(). {match_id=}, {xuids=}\n{ex}')
    except Exception as ex:
        logging.error(f'Error in skill.get_match_result(). {match_id=}, {xuids=}\n{ex}')


def create_match_tab_sep_vals(match_stats: MatchStats) -> str:
    mi = match_stats.match_info
    mv = mi.map_variant
    gv = mi.ugc_game_variant
    p = mi.playlist
    mmp = mi.playlist_map_mode_pair
    if p is not None:
        p_asset_id = p.asset_id
        p_version_id = p.version_id
    else:
        p_asset_id = p_version_id = None
    if mmp is not None:
        mmp_asset_id = mmp.asset_id
        mmp_version_id = mmp.version_id
    else:
        mmp_asset_id = mmp_version_id = None
    return _to_tab_separated_values((
        match_stats.match_id,
        mi.start_time,
        mi.end_time,
        mi.duration.total_seconds(),
        mi.lifecycle_mode.value,
        mi.game_variant_category.value,
        mi.level_id,
        mv.asset_id,
        mv.version_id,
        gv.asset_id,
        gv.version_id,
        p_asset_id,
        p_version_id,
        mi.playlist_experience.value if mi.playlist_experience is not None else None,
        mmp_asset_id,
        mmp_version_id,
        mi.playable_duration.total_seconds(),
    ))


def iter_team_stats_tab_sep_vals(match_stats: MatchStats):
    for team in match_stats.teams:
        core = team.stats.core_stats
        yield _to_tab_separated_values((
            match_stats.match_id,
            team.team_id,
            team.outcome.value,
            team.rank,
            core.score,
            core.personal_score,
            core.rounds_won,
            core.rounds_lost,
            core.rounds_tied,
            core.kills,
            core.deaths,
            core.assists,
            core.suicides,
            core.betrayals,
            core.grenade_kills,
            core.headshot_kills,
            core.melee_kills,
            core.power_weapon_kills,
            core.shots_fired,
            core.shots_hit,
            core.damage_dealt,
            core.damage_taken,
            core.callout_assists,
            core.driver_assists,
            core.emp_assists,
            core.vehicle_destroys,
            core.hijacks,
            core.max_killing_spree,
        ))


def iter_player_xuids(match_stats: MatchStats):
    for player in match_stats.players:
        if player.player_type == PlayerType.Human:
            yield player.player_id


def iter_player_stats_tab_sep_vals(match_stats: MatchStats):
    for player in match_stats.players:
        if player.player_type == PlayerType.Bot:
            xuid = int(float(player.player_id[4:-1]))
        else:
            xuid = int(util.unwrap_xuid(player.player_id))
        pinfo = player.participation_info
        for ptstats in player.player_team_stats:
            core = ptstats.stats.core_stats
            yield _to_tab_separated_values((
                match_stats.match_id,
                xuid,
                player.last_team_id,
                player.outcome.value,
                player.rank,
                pinfo.first_joined_time,
                pinfo.last_leave_time,
                pinfo.present_at_beginning,
                pinfo.joined_in_progress,
                pinfo.left_in_progress,
                pinfo.present_at_completion,
                pinfo.time_played.total_seconds(),
                pinfo.confirmed_participation,
                ptstats.team_id,
                core.score,
                core.personal_score,
                core.rounds_won,
                core.rounds_lost,
                core.rounds_tied,
                core.kills,
                core.deaths,
                core.assists,
                core.suicides,
                core.betrayals,
                core.grenade_kills,
                core.headshot_kills,
                core.melee_kills,
                core.power_weapon_kills,
                core.shots_fired,
                core.shots_hit,
                core.damage_dealt,
                core.damage_taken,
                core.callout_assists,
                core.driver_assists,
                core.emp_assists,
                core.vehicle_destroys,
                core.hijacks,
                core.max_killing_spree,
            ))


def iter_skill_tab_sep_vals(match_skill: MatchSkillInfo, match_id: uuid.UUID):
    for pskill in match_skill.value:
        if pskill.result_code > 0:
            logging.warning('result code "%s" when requesting match "%s", player "%s":\n%s',
                            pskill.result_code, match_id, pskill.id, pskill)
        r = pskill.result
        sp = r.stat_performances
        yield _to_tab_separated_values((
            match_id,
            int(util.unwrap_xuid(pskill.id)),
            r.team_id,
            pskill.result_code,
            r.team_mmr,
            r.rank_recap.pre_match_csr.value,
            r.rank_recap.post_match_csr.value,
            sp.kills.expected,
            sp.deaths.expected,
        ))


def _to_tab_separated_values(tup: tuple[Any, ...]) -> str:
    out = '\t'.join('' if item is None else str(item) for item in tup)
    return f'{out}\n'

