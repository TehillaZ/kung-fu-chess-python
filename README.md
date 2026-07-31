# Kung Fu Chess (Python)

Real-time kung-fu chess engine with a graphic OpenCV UI.

## Requirements

- Python 3.10+
- OpenCV for the graphic UI:

```bash
pip install -r UI/requirements.txt
```

## Run the graphic game

From the project root:

```bash
py UI/main.py
```

- Click a piece, then click a destination square.
- Press `Q` or `Esc` to quit.

## Run the text engine

```bash
py main.py < your_script.txt
```

## Run the multiplayer server

```bash
pip install -r server/requirements.txt
py server/app.py
```

Clients connect over WebSocket to `ws://localhost:8765/room/<room_id>`. The
first two connections into a room are assigned white/black; everyone after
that is a read-only viewer. A room's clock pauses whenever a seat is empty
and resumes once both are filled again. Game/participant/move history is
recorded to `kfchess.db` (SQLite) at the project root.

## Tests

```bash
py -m unittest discover -s tests -p "test_*.py" -v
```

## Project layout

| Path | Purpose |
|------|---------|
| `kungfu_chess/` | Engine, model, rules, persistence |
| `UI/` | OpenCV renderer and sprites |
| `server/` | WebSocket multiplayer server (rooms, roles, protocol) |
| `assets/` | Board and piece images (`pieces1`) |
| `tests/` | Unit and integration tests |
| `main.py` | Text / DSL entry point |
| `board.csv` | Standard starting position, shared by `UI/main.py` and `server/app.py` |
