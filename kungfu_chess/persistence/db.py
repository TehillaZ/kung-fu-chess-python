import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    rows INTEGER NOT NULL,
    cols INTEGER NOT NULL,
    status TEXT NOT NULL,
    winner_color TEXT,
    ended_at TEXT
);

CREATE TABLE IF NOT EXISTS game_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL REFERENCES games(id),
    connection_id TEXT NOT NULL,
    color TEXT,
    role TEXT NOT NULL,
    joined_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS moves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL REFERENCES games(id),
    seq INTEGER NOT NULL,
    color TEXT NOT NULL,
    piece_token TEXT NOT NULL,
    from_row INTEGER NOT NULL,
    from_col INTEGER NOT NULL,
    to_row INTEGER NOT NULL,
    to_col INTEGER NOT NULL,
    clock_ms INTEGER NOT NULL,
    accepted INTEGER NOT NULL,
    reason TEXT NOT NULL
);
"""


def connect(path=":memory:"):
    """Open a SQLite connection with the schema applied, WAL mode for file DBs."""
    connection = sqlite3.connect(str(path))
    if str(path) != ":memory:":
        connection.execute("PRAGMA journal_mode=WAL")
    connection.executescript(SCHEMA)
    connection.commit()
    return connection
