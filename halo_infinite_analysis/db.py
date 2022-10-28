

import contextlib
import pathlib
from typing import Any, TextIO
import uuid

import psycopg2
import psycopg2.extensions
import psycopg2.extras
import psycopg2.sql


Conn = psycopg2.extensions.connection
Cursor = psycopg2.extensions.cursor

SQL_DIR = pathlib.Path(__file__).parent / 'sql'
TABLES_DIR = SQL_DIR / 'tables'

psycopg2.extras.register_uuid()


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
    for fpath in TABLES_DIR.iterdir():
        cur.execute(fpath.read_text())
    conn.commit()


def create_match_queues(conn: Conn, schema: str, match_ids: list[tuple[uuid.UUID]]):
    sql = """
        INSERT INTO match
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    template = '(%s)'
    _execute_values(conn, sql, schema, template, match_ids)


def get_match_queues(conn: Conn, schema: str) -> list[uuid.UUID]:
    sql = """
        SELECT id
        FROM match
        WHERE NOT is_completed
        ORDER BY rand
        LIMIT 100
    """
    rows = _execute_fetch_all(conn, sql, schema)
    return [r[0] for r in rows]


def update_match_queue(conn: Conn, schema: str, match_ids: list[uuid.UUID]):
    sql = """
        UPDATE match_queue
        SET is_completed = true
        WHERE id IN %s
    """
    _execute(conn, sql, schema, (match_ids,))


def create_player_queues(conn: Conn, schema: str, player_xuids: list[tuple[int]]):
    sql = """
        INSERT INTO player_queue
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    template = '(%s)'
    _execute_values(conn, sql, schema, template, player_xuids)


def get_player_queue_needing_history(conn: Conn, schema: str):
    sql = """
        SELECT xuid
        FROM player_queue
        WHERE NOT history
        ORDER BY rand
        LIMIT 100
    """
    rows = _execute_fetch_all(conn, sql, schema)
    return [r[0] for r in rows]


def update_player_queue_history(conn: Conn, schema: str, player_xuids: list[int]):
    sql = """
        UPDATE player_queue
        SET history = true
        WHERE xuid IN %s
    """
    _execute(conn, sql, schema, (player_xuids,))


def create_matches(conn: Conn, schema: str, stream: TextIO):
    _copy_from(conn, stream, schema, 'match')


def create_team_stats(conn: Conn, schema: str, stream: TextIO):
    _copy_from(conn, stream, schema, 'team_stats')


def create_player_stats(conn: Conn, schema: str, stream: TextIO):
    _copy_from(conn, stream, schema, 'player_stats')


def create_skill(conn: Conn, schema: str, stream: TextIO):
    _copy_from(conn, stream, schema, 'skill')


def _set_schema(cur: Cursor, schema: str):
    cur.execute('SET search_path = %s', (schema,))


def _execute(conn: Conn, sql: str, schema: str | None = None, params: tuple[Any, ...] | None = None):
    cur = conn.cursor()
    if schema is not None:
        _set_schema(cur, schema)
    cur.execute(sql, params)
    conn.commit()


def _execute_fetch_all(conn: Conn, sql:str, schema: str, params: tuple[Any, ...] | None = None):
    cur = conn.cursor()
    _set_schema(cur, schema)
    cur.execute(sql, params)
    return cur.fetchall()


def _execute_values(conn: Conn, sql: str, schema: str, template: str, values: list[tuple[Any, ...]]):
    cur = conn.cursor()
    _set_schema(cur, schema)
    psycopg2.extras.execute_values(cur, sql, values, template)
    conn.commit()


def _copy_from(conn: Conn, stream: TextIO, schema: str, table: str):
    cur = conn.cursor()
    _set_schema(cur, schema)
    stream.seek(0)
    cur.copy_from(stream, table)
    conn.commit()

