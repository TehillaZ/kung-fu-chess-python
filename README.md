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

## Tests

```bash
py -m unittest discover -s tests -p "test_*.py" -v
```

## Project layout

| Path | Purpose |
|------|---------|
| `kungfu_chess/` | Engine, model, rules |
| `UI/` | OpenCV renderer and sprites |
| `assets/` | Board and piece images (`pieces1`) |
| `tests/` | Unit and integration tests |
| `main.py` | Text / DSL entry point |
