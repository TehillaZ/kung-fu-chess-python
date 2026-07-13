kungfu_chess/
|
+-- model/
|   +-- position.py
|   +-- piece.py
|   +-- board.py
|   +-- game_state.py
|
+-- rules/
|   +-- piece_rules.py
|   +-- rule_engine.py
|   +-- rules_loader.py
|   +-- path_utils.py
|   +-- rules.json
|
+-- realtime/
|   +-- motion.py
|   +-- real_time_arbiter.py
|
+-- engine/
|   +-- game_engine.py
|
+-- input/
|   +-- board_mapper.py
|   +-- controller.py
|
+-- io/
|   +-- board_parser.py
|   +-- board_printer.py
|
+-- view/
|   +-- renderer.py
|   +-- image_view.py
|
+-- texttests/
|   +-- script_parser.py
|   +-- script_runner.py
|
+-- app.py
|
tests/
+-- unit/
    +-- test_kfchess.py

Entry point:
- main.py -> p_input.py -> kungfu_chess/texttests/script_runner.py
