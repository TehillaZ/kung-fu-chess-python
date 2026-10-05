# Kung Fu Chess — Architecture

## Package layout

```
kungfu_chess/
  model/
    position.py
    piece.py
    piece_factory.py
    board.py
    game_state.py
    game_snapshot.py
  rules/
    piece_rules.py
    rule_engine.py
    rules_loader.py
    path_utils.py
    rules.json
  realtime/
    motion.py
    arrival_events.py
    real_time_arbiter.py
  engine/
    game_engine.py
    move_result.py
  input/
    board_mapper.py
    controller.py
  io/
    board_parser.py
    board_printer.py
  view/
    renderer.py
  texttests/
    script_runner.py
  app.py
```

## Entry points

| Entry | Purpose |
|-------|---------|
| `main.py` → `p_input.py` | Text DSL via stdin (`Board`, `click`, `wait`, `print board`) |
| `kungfu_chess/app.py` | Text DSL via stdin (same as `main.py`) |

## Layer responsibilities

| Layer | Role |
|-------|------|
| **Model** | `Position`, `Piece`, `Board`, `GameState`, `GameSnapshot` — occupancy and lifecycle only |
| **PieceRules** | Stateless legal-destination geometry per piece type |
| **RuleEngine** | Read-only validation → `MoveValidation` |
| **RealTimeArbiter** | `Motion` timing, arrival resolution, capture events |
| **GameEngine** | Guards, `request_move`, `wait`, `snapshot` |
| **Controller** | Clicks → `request_move`; selection state |
| **BoardMapper** | Pixel → cell |
| **BoardParser / BoardPrinter** | Text I/O |
| **ScriptRunner** | Drives public command path for text tests |
| **Renderer** | Formats read-only `GameSnapshot` as text |

Dependency direction: **Model ← Rules ← Engine ← Controller/Tests**. View reads snapshots only.

## Test layout

```
tests/
  unit/
    test_position.py
    test_piece.py
    test_board.py
    test_board_parser.py
    test_board_printer.py
    test_board_mapper.py
    test_piece_rules.py
    test_rule_engine.py
    test_controller.py
    test_game_engine.py
    test_game_engine_integration.py
    test_real_time_arbiter.py
    test_invalid_moves.py
    test_game_snapshot.py
    test_renderer.py
    test_script_runner.py
    test_pawn_movement.py
    test_knight_movement.py
  integration/
    scripts/*.kfc
    test_text_scripts.py
```

Run all tests:

```
py -m unittest discover -s tests -p "test_*.py" -v
```
