

import contextlib
import datetime as dt
import pathlib
from typing import Any, TextIO
import uuid

import psycopg2
import psycopg2.extensions
import psycopg2.extras
import psycopg2.sql


Conn = psycopg2.extensions.connection
Cursor = psycopg2.extensions.cursor

psycopg2.extras.register_uuid()

SQL_DIR = pathlib.Path(__file__).parent / 'sql'
TABLE_CREATE_ORDER = (
    'game_variant_category',
    'game_variant',
    'level',
    'lifecycle_mode',
    'map_variant',
    'match_dump',
    'match_queue',
    'outcome',
    'player_dump',
    'player_queue',
    'player',
    'playlist_experience',
    'playlist_map_mode_pair',
    'playlist',
    'skill_dump',
    'team_dump',
    'match',
    'player_skill',
    'player_stat',
    'team_skill',
    'team_stat',
)
VIEW_CREATE_ORDER = (
    'vw_match',
    'vw_player',
    'vw_team',
)


@contextlib.contextmanager
def connect(name: str, user: str, password: str, host: str = 'localhost', port: int = 5432):
    conn = psycopg2.connect(dbname=name, user=user, password=password, host=host, port=port)
    try:
        yield conn
    finally:
        conn.close()


def create_schema(conn: Conn, schema: str):
    ident = psycopg2.sql.Identifier(schema)
    sql = psycopg2.sql.SQL('CREATE SCHEMA IF NOT EXISTS {}').format(ident)
    _execute(conn, sql)


def create_tables(conn: Conn, schema: str):
    cur = conn.cursor()
    _set_schema(cur, schema)
    for name in TABLE_CREATE_ORDER:
        pth = SQL_DIR / f'tables/{name}.sql'
        cur.execute(pth.read_text())
    conn.commit()


def create_views(conn: Conn, schema: str):
    cur = conn.cursor()
    _set_schema(cur, schema)
    for name in VIEW_CREATE_ORDER:
        pth = SQL_DIR / f'views/{name}.sql'
        cur.execute(pth.read_text())
    conn.commit()


def create_match_queues(conn: Conn, schema: str, match_ids: list[tuple[uuid.UUID]]):
    sql = """
        INSERT INTO match_queue
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    template = '(%s)'
    _execute_values(conn, sql, schema, template, match_ids)


def get_match_queues(conn: Conn, schema: str, limit: int) -> list[uuid.UUID]:
    sql = """
        SELECT id
        FROM match_queue
        WHERE NOT is_completed
        ORDER BY rand
        LIMIT %s
    """
    rows = _execute_fetch_all(conn, sql, schema, (limit,))
    return [r[0] for r in rows]


def update_match_queue(conn: Conn, schema: str, match_ids: list[uuid.UUID]):
    sql = """
        UPDATE match_queue
        SET is_completed = true
        WHERE id IN %s
    """
    _execute(conn, sql, schema, (tuple(match_ids),))


def create_player_queues(conn: Conn, schema: str, player_xuids: list[tuple[int]]):
    sql = """
        INSERT INTO player_queue
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    template = '(%s)'
    _execute_values(conn, sql, schema, template, player_xuids)


def get_player_queue_needing_history(conn: Conn, schema: str, limit: int) -> list[int]:
    sql = """
        SELECT xuid
        FROM player_queue
        WHERE NOT history
        ORDER BY rand
        LIMIT %s
    """
    rows = _execute_fetch_all(conn, sql, schema, (limit,))
    return [r[0] for r in rows]


def update_player_queue_history(conn: Conn, schema: str, player_xuids: list[int]):
    sql = """
        UPDATE player_queue
        SET history = true
        WHERE xuid IN %s
    """
    _execute(conn, sql, schema, (tuple(player_xuids),))


def create_matches(conn: Conn, schema: str, stream: TextIO):
    _copy_from(conn, stream, schema, 'match_dump')


def create_team_stats(conn: Conn, schema: str, stream: TextIO):
    _copy_from(conn, stream, schema, 'team_dump')


def create_player_stats(conn: Conn, schema: str, stream: TextIO):
    _copy_from(conn, stream, schema, 'player_dump')


def create_skill(conn: Conn, schema: str, stream: TextIO):
    _copy_from(conn, stream, schema, 'skill_dump')


def clean_dumped_data(conn: Conn, schema: str):
    sql = (SQL_DIR / 'clean.sql').read_text()
    _execute(conn, sql, schema)


def delete_dumped_data(conn: Conn, schema: str):
    sql = (SQL_DIR / 'delete.sql').read_text()
    _execute(conn, sql, schema)


def get_game_variants(conn: Conn, schema: str) -> list[tuple[uuid.UUID, uuid.UUID, str | None]]:
    return _get_metadata(conn, schema, 'game_variant')


def get_map_variants(conn: Conn, schema: str) -> list[tuple[uuid.UUID, uuid.UUID, str | None]]:
    return _get_metadata(conn, schema, 'map_variant')


def get_playlists(conn: Conn, schema: str) -> list[tuple[uuid.UUID, uuid.UUID, str | None]]:
    return _get_metadata(conn, schema, 'playlist')


def get_playlist_map_mode_pairs(conn: Conn, schema: str) -> list[tuple[uuid.UUID, uuid.UUID, str | None]]:
    return _get_metadata(conn, schema, 'playlist_map_mode_pair')


def update_metadata(conn: Conn, schema: str, table: str, records: list[tuple[str, uuid.UUID, uuid.UUID]]):
    ident = psycopg2.sql.Identifier(table)
    txt = 'UPDATE {} SET name = %s WHERE asset_id = %s AND version_id = %s'
    sql = psycopg2.sql.SQL(txt).format(ident)  # type: ignore
    _execute_many(conn, sql, schema, records)


def get_latest_match_date(conn: Conn, schema: str) -> dt.datetime | None:
    sql = """
        SELECT max(start_time)
        FROM (
            SELECT start_time
            FROM match_dump

            UNION ALL

            SELECT start_time
            FROM match
        ) t
    """
    rows = _execute_fetch_all(conn, sql, schema)
    return rows[0][0]


def _set_schema(cur: Cursor, schema: str):
    cur.execute('SET search_path = %s', (schema,))


def _execute(conn: Conn, sql: str | psycopg2.sql.Composable, schema: str | None = None, params: tuple[Any, ...] | None = None):
    cur = conn.cursor()
    if schema is not None:
        _set_schema(cur, schema)
    cur.execute(sql, params)
    conn.commit()


def _execute_many(conn: Conn, sql: str | psycopg2.sql.Composable, schema: str, params: list[tuple[Any, ...]]):
    cur = conn.cursor()
    _set_schema(cur, schema)
    cur.executemany(sql, params)
    conn.commit()


def _execute_fetch_all(conn: Conn, sql: str | psycopg2.sql.Composable, schema: str, params: tuple[Any, ...] | None = None):
    cur = conn.cursor()
    _set_schema(cur, schema)
    cur.execute(sql, params)
    return cur.fetchall()


def _get_metadata(conn: Conn, schema: str, table: str) -> list[tuple[uuid.UUID, uuid.UUID, str | None]]:
    ident = psycopg2.sql.Identifier(table)
    txt = 'SELECT DISTINCT asset_id, version_id, name FROM {}'
    sql = psycopg2.sql.SQL(txt).format(ident)  # type: ignore
    rows = _execute_fetch_all(conn, sql, schema)
    return [(r[0], r[1], r[2]) for r in rows]


def _execute_values(conn: Conn, sql: str, schema: str, template: str, values: list[tuple[Any, ...]]):
    cur = conn.cursor()
    _set_schema(cur, schema)
    psycopg2.extras.execute_values(cur, sql, values, template)
    conn.commit()


def _copy_from(conn: Conn, stream: TextIO, schema: str, table: str):
    cur = conn.cursor()
    _set_schema(cur, schema)
    stream.seek(0)
    cur.copy_from(stream, table, null='', sep='\t')
    conn.commit()

