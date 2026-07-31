"""
Kung Fu Chess multiplayer server.

Run from project root:
  py server/app.py

Clients connect to ws://<host>:<port>/room/<room_id>. The first two
connections into a room become the white/black players; everyone after
that is a read-only viewer. A room's clock only advances while both
seats are filled (see server/room.py for the pause-on-disconnect rule).
"""

import asyncio
import json
import sys
import uuid
from pathlib import Path

import websockets
from websockets.exceptions import ConnectionClosed

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kungfu_chess.io.board_csv import load_board_csv
from kungfu_chess.model.piece import COLOR_BLACK, COLOR_WHITE, KIND_KING
from kungfu_chess.persistence.db import connect as connect_db
from kungfu_chess.persistence.repository import GameRepository
from server.protocol import (
    ProtocolError,
    decode_client_message,
    encode_error,
    encode_role,
    encode_snapshot,
)
from server.room_manager import RoomManager

HOST = "localhost"
PORT = 8765
TICK_MS = 50
BOARD_CSV_PATH = PROJECT_ROOT / "board.csv"
DB_PATH = PROJECT_ROOT / "kfchess.db"

# connection_id (uuid str) -> live socket. Room only ever sees the id,
# never the socket, so this mapping lives at the transport boundary.
CONNECTION_SOCKETS = {}
# room_id -> the asyncio task currently ticking/broadcasting that room.
ROOM_TASKS = {}


def room_id_from_path(path):
    parts = [part for part in path.split("/") if part]
    if len(parts) == 2 and parts[0] == "room":
        return parts[1]
    return None


def determine_winner(snapshot):
    kings_present = {
        piece.color for piece in snapshot.pieces if piece.kind == KIND_KING
    }
    if COLOR_WHITE not in kings_present:
        return COLOR_BLACK
    if COLOR_BLACK not in kings_present:
        return COLOR_WHITE
    return None


async def broadcast(room, message):
    payload = json.dumps(message)
    for connection_id in room.connections():
        socket = CONNECTION_SOCKETS.get(connection_id)
        if socket is None:
            continue
        try:
            await socket.send(payload)
        except ConnectionClosed:
            pass


async def room_loop(room, repository):
    """Ticks and broadcasts while both seats are filled; exits on pause or game end."""
    try:
        while room.is_active():
            room.tick(TICK_MS)
            snapshot = room.snapshot()
            await broadcast(room, encode_snapshot(snapshot))

            if snapshot.game_over:
                if repository is not None and room.game_id is not None:
                    repository.end_game(room.game_id, determine_winner(snapshot))
                break

            await asyncio.sleep(TICK_MS / 1000)
    finally:
        ROOM_TASKS.pop(room.room_id, None)


def ensure_room_loop(room, repository):
    if room.room_id in ROOM_TASKS or not room.is_active():
        return
    ROOM_TASKS[room.room_id] = asyncio.create_task(room_loop(room, repository))


async def handle_connection(connection, room_manager, repository):
    room_id = room_id_from_path(connection.request.path)
    if room_id is None:
        await connection.close(code=4000, reason="expected /room/<id>")
        return

    connection_id = str(uuid.uuid4())
    CONNECTION_SOCKETS[connection_id] = connection

    room = room_manager.get_or_create(room_id)
    role = room.join(connection_id)

    try:
        await connection.send(json.dumps(encode_role(role)))
        ensure_room_loop(room, repository)

        async for raw in connection:
            try:
                message = decode_client_message(raw)
            except ProtocolError as exc:
                await connection.send(json.dumps(encode_error(str(exc))))
                continue

            room.request_move(connection_id, message["from"], message["to"])
    except ConnectionClosed:
        pass
    finally:
        room.leave(connection_id)
        CONNECTION_SOCKETS.pop(connection_id, None)
        room_manager.remove_if_empty(room_id)


async def main():
    board_string = load_board_csv(BOARD_CSV_PATH)
    repository = GameRepository(connect_db(DB_PATH))
    room_manager = RoomManager(board_string, repository=repository)

    async def bound_handler(connection):
        await handle_connection(connection, room_manager, repository)

    async with websockets.serve(bound_handler, HOST, PORT):
        print(f"KFChess server listening on ws://{HOST}:{PORT}/room/<id>")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
