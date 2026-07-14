# Kung Fu Chess — Alignment Plan

This plan maps the course specification (`kung_fu_chess_en.docx`) onto the current codebase and defines the ordered steps required to make the system match the **common route** described in the document.

---

## Target Summary (from the spec)

### Game rules (common route)
- Rectangular board from text; tokens: `.`, `wK`, `bR`, etc.
- Pieces move by chess patterns at fixed speed (`CELL_SIZE = 100`, **1000 ms per cell**).
- Logical board updates **only on arrival**; moving pieces stay on source cell until then.
- **One active motion at a time** — second move rejected with `"motion_in_progress"`.
- No check, checkmate, castling, en passant, or **promotion**.
- Pawn: one step forward, diagonal capture only; **no two-step start move**.
- King can be captured; king capture **ends the game** (`"game_over"`).
- Text DSL: **`Board`**, **`click`**, **`wait`**, **`print board`** only.

### Architecture (layered, testable)
| Layer | Responsibility |
|-------|----------------|
| **Model** | `Position`, `Piece`, `Board`, `GameState` — occupancy & lifecycle only |
| **PieceRules** | Stateless legal-destination geometry per piece type |
| **RuleEngine** | Read-only validation → `MoveValidation(is_valid, reason)` |
| **RealTimeArbiter** | `Motion` objects, time advancement, arrival & capture |
| **GameEngine** | Application service: guards, `request_move`, `wait`, `snapshot` |
| **Controller** | Clicks → commands; selection state; no legality or board mutation |
| **BoardMapper** | Pixel → cell (`col = x // 100`, `row = y // 100`) |
| **Text I/O** | `BoardParser`, `BoardPrinter` (shared, not inside `texttests`) |
| **TextTestRunner** | Drives public command path only |
| **Renderer** | Draws read-only `GameSnapshot` only |

### Public API (spec §20)
```
BoardParser.parse(text) -> Board
BoardPrinter.print(snapshot) -> text
BoardMapper.pixel_to_cell(x, y) -> Position | None
Controller.click(x, y) -> ControllerResult
GameEngine.request_move(source, destination) -> MoveResult
GameEngine.wait(ms) -> None
GameEngine.snapshot() -> GameSnapshot
RuleEngine.validate_move(board, source, destination) -> MoveValidation
RealTimeArbiter.has_active_motion() -> bool
RealTimeArbiter.start_motion(...) -> None
RealTimeArbiter.advance_time(ms) -> ArrivalEvents
```

---

## Current State vs Spec

### Already in place (partial or complete)
- [x] Package skeleton under `kungfu_chess/` with correct top-level folders
- [x] `BoardParser` / `BoardPrinter` / `ScriptRunner` / `main.py` entry chain
- [x] `Position` value object with equality
- [x] `Board` with string-grid occupancy, `move_piece`, bounds checks
- [x] `BoardMapper` pixel mapping (`cell_size = 100`)
- [x] `RuleEngine` + `piece_rules` validators for all piece types
- [x] `RealTimeArbiter` + `Motion` with 1000 ms/cell timing
- [x] Logical board unchanged until arrival
- [x] Capture on arrival, king capture → `game_over`
- [x] Controller click selection (first click select, second click move)
- [x] Unit + text integration tests in `tests/unit/test_kfchess.py` (41 passing)

### Deviations from common route (must fix)
| Area | Current | Spec requires |
|------|---------|---------------|
| Motion policy | Multiple simultaneous pending motions | **One active motion**; reject with `"motion_in_progress"` |
| GameEngine API | `execute_click` / `execute_wait`; no `request_move` / `MoveResult` | `request_move` → `MoveResult`; guards before `RuleEngine` |
| Validation results | String reasons (`"illegal_move"`) | `MoveValidation` with stable reasons: `outside_board`, `empty_source`, `friendly_destination`, `illegal_piece_move`, `ok` |
| Pawn rules | Two-step from start rank + promotion to queen | **No** two-step, **no** promotion |
| DSL commands | `jump` command supported | **Only** `Board`, `click`, `wait`, `print board` |
| Knight movement | Special airborne / in-place jump capture logic | L-shaped jumps ignoring blockers; **no** separate `jump` DSL |
| Motion ownership | `Controller.pending_motions` | `RealTimeArbiter` owns active motions |
| Model | String tokens on grid; `Piece` class unused by `Board` | `Piece` with `id`, `color`, `kind`, `cell`, `state` (`idle`/`moving`/`captured`) |
| PieceRules API | `is_legal_move(piece, start, end, board) -> bool` | `legal_destinations(board, piece) -> set[Position]` |
| Snapshot / UI | `Renderer` stub; no `GameSnapshot` | `GameEngine.snapshot()` + thin renderer |
| Tests | Single `test_kfchess.py` | Per-component unit tests + `integration/scripts/*.kfc` |
| Opposite-color route conflicts | Custom delay / collision logic | Common route: **not required** (extra-route feature) |

---

## Implementation Steps (spec iteration order)

Each step follows: **requirement → failing tests → implementation → refactor → commit**.

---

### Step 0 — Baseline & inventory
**Goal:** Freeze current behavior and document gaps.

1. Run full test suite; record passing count as regression baseline.
2. List grader / course tests that fail against common-route rules.
3. Mark features to **remove or gate** (simultaneous motion, `jump` DSL, pawn promotion, pawn two-step, airborne capture extras).
4. Keep `ChessGameSimulator` as a thin test alias until `GameEngine` API is finalized.

**Done when:** Baseline documented; team agrees common route is the target.

**Status:** Complete — see `BASELINE.md`.

---

### Step 1 — Model alignment (Iteration 0–1)
**Goal:** Pure model matches spec.

1. **`Position`**
   - Add `__repr__` for readable test failures.
   - Unit tests: equality, inequality, repr.

2. **`Piece`**
   - Fields: `id`, `color`, `kind`, `cell: Position`, `state: idle | moving | captured`.
   - `PieceFactory` or `BoardParser` assigns stable unique IDs.
   - Unit tests: lifecycle transitions; no timing/path on `Piece`.

3. **`Board`**
   - Store `Piece` objects by position (or indexed grid referencing pieces).
   - Methods: `add_piece`, `remove_piece`, `piece_at`, `is_inside`, `move_piece` (post-validation only).
   - Reject duplicate occupancy and duplicate IDs.
   - Unit tests: dimensions, lookup, move, capture removal.

4. **`BoardParser`**
   - Parse text → `Board` with `Piece` instances.
   - Keep existing error codes: `ERROR EMPTY_BOARD`, `ERROR ROW_WIDTH_MISMATCH`, `ERROR UNKNOWN_TOKEN`.

5. **`BoardPrinter`**
   - Print from `Board` or `GameSnapshot` (logical occupancy only).
   - Round-trip test: parse → print → compare.

**Done when:** Model tests pass; no pixels/rules/timing in model layer.

**Status:** Complete — 23 new model tests; 64 total passing. `Board` stores `Piece` objects; token API preserved for upper layers.

---

### Step 2 — Input layer (Iteration 2)
**Goal:** Clicks map to cells; selection policy matches spec.

1. **`BoardMapper.pixel_to_cell(x, y) -> Position | None`**
   - Outside board → `None`.
   - Unit tests for column/row mapping examples from spec.

2. **`Controller`**
   - `click(x, y)` only — no direct `RuleEngine` or `Board.move_piece`.
   - Selection rules:
     - First click on piece → select.
     - First click on empty → ignore.
     - No selection + outside click → ignore.
     - Selection + outside click → clear selection, no command.
     - Second in-board click → call `GameEngine.request_move(source, dest)`; always clear selection.
   - Unit tests with fake `GameEngine` recording calls.

**Done when:** Controller tests pass; no motion or validation inside controller.

**Status:** Complete — 16 new input-layer tests; 80 total passing. `Controller` delegates to `GameEngine.request_move`; `BoardMapper.pixel_to_cell` added.

---

### Step 3 — Piece rules & RuleEngine (Iteration 3 + 7)
**Goal:** Stateless geometry per piece; stable validation API.

1. **Refactor `PieceRules`**
   - Per piece type: `legal_destinations(board, piece) -> set[Position]`.
   - Rook → bishop → queen → knight → king → pawn (spec order).
   - Pawn: one forward step, diagonal capture; **remove** two-step and promotion logic.

2. **`RuleEngine.validate_move(board, source, dest) -> MoveValidation`**
   - Checks: `outside_board`, `empty_source`, `friendly_destination`, delegate to piece rule, else `illegal_piece_move`.
   - Valid → `reason="ok"`.
   - Read-only — never mutates `Board`.

3. **Unit tests per piece type** (spec §7 list) in dedicated files:
   - `tests/unit/test_piece_rules.py`
   - `tests/unit/test_rule_engine.py`

**Done when:** All piece rule tests pass; pawn matches simplified spec.

**Status:** Complete — `legal_destinations(board, piece)` added, `MoveValidation` added, pawn simplified (no two-step, no promotion), and 16 new Step 3 tests added. 96 total tests passing.

---

### Step 4 — GameEngine command path without time (Iteration 4)
**Goal:** Explicit command boundary before real-time behavior.

1. Add **`MoveResult(is_accepted, reason)`** and **`MoveValidation(is_valid, reason)`**.
2. Implement **`GameEngine.request_move(source, destination) -> MoveResult`**:
   - If `game_over` → reject `"game_over"`.
   - If `arbiter.has_active_motion()` → reject `"motion_in_progress"`.
   - Else delegate to `RuleEngine`.
   - On valid: call `arbiter.start_motion(...)`; return `"ok"`.
   - On invalid: board unchanged, no motion started.
3. Wire `Controller.click` → `GameEngine.request_move`.
4. **No board mutation on click** until time advances (next step).
5. Unit tests: `tests/unit/test_game_engine.py` with fakes for `RuleEngine` and `RealTimeArbiter`.

**Done when:** Command routing tests pass; invalid moves leave board unchanged.

**Status:** Complete — `request_move` uses `MoveValidation`, `RealTimeArbiter.has_active_motion()` / `start_motion()`, motion ownership moved to arbiter, and 6 new `test_game_engine.py` tests added. 102 total tests passing.

---

### Step 5 — Real-time movement (Iteration 5)
**Goal:** Deterministic timing; one motion; logical board updates on arrival.

1. Move **`pending_motions`** from `Controller` to **`RealTimeArbiter`**.
2. Implement:
   - `has_active_motion() -> bool`
   - `start_motion(piece, source, dest)`
   - `advance_time(ms) -> ArrivalEvents`
3. Timing: `N` cells = `N × 1000 ms`; diagonal uses cell-step count.
4. **`GameEngine.wait(ms)`** delegates to `arbiter.advance_time`; applies arrivals to `Board`.
5. **Enforce single motion:** second `request_move` while active → `"motion_in_progress"`.
6. Remove simultaneous opposite-color motion / route-delay logic (extra-route behavior).
7. Text test (spec Iteration 5):
   ```
   Board:
   . wR .
   . . .
   . . bK
   Commands:
   click 150 50
   click 150 250
   wait 1000
   print board
   . wR .
   . . .
   . . bK
   wait 1000
   print board
   . . .
   . . .
   . wR bK
   ```
8. Unit tests: `tests/unit/test_real_time_arbiter.py` — 999 ms vs 1000 ms, partial waits, accumulation.

**Done when:** One-motion policy enforced; timing tests pass.

**Status:** Complete — `ArrivalEvents` added, `advance_time()` returns arrival events, motions depart immediately (route-delay logic removed), `GameEngine.wait` applies arrivals via arbiter, spec Iteration 5 text test added, and 7 new `test_real_time_arbiter.py` tests. **109** total tests passing.

---

### Step 6 — Captures & game over (Iteration 6)
**Goal:** Capture on arrival; king capture ends game.

1. **Arrival resolution (atomic):** remove from source → capture enemy at dest → place mover → set captured `Piece.state` → report king capture.
2. **`GameEngine`:** on king capture, set `game_over`; clear pending motions; ignore further `request_move`.
3. Remove or isolate **airborne jump capture** and **`jump` DSL** (not in common route).
4. Knight moves: L-shape at 1000 ms total (treat as one jump distance = max(Δrow, Δcol) or spec-defined cell count — align with grader).
5. Text + unit tests for capture and post-game-over immutability.

**Done when:** Spec Iteration 6 text test passes; `game_over` guard tested.

**Status:** Complete — arrival resolution simplified (capture on `board.move_piece`, king capture via `ArrivalEvents`), airborne/in-place jump logic removed from arbiter, `request_jump`/`execute_jump`/`handle_jump` removed, `jump` DSL handler removed from `ScriptRunner`, extra-route collision tests replaced, spec Iteration 6 capture text test added, and 6 new capture/game-over tests. **113** total tests passing.

---

### Step 7 — Invalid moves & error stability (Iteration 8)
**Goal:** Predictable negative behavior.

1. Audit all rejection paths; map each to owning layer.
2. Ensure invalid click sequences never crash and never mutate board.
3. Selection clears after every second in-board click (legal or illegal).
4. Text test: blocked rook path → unchanged board after `wait`.
5. Unit tests assert exact `reason` strings for each rejection type.

**Done when:** Negative tests pass; reasons stable and documented.

**Status:** Complete — all `MoveResult` / `MoveValidation` rejection reasons covered in unit tests, illegal clicks leave board unchanged and clear selection, spec Iteration 8 blocked-rook text test added (`test_invalid_moves.py`), and `GameEngine.wait()` / `click()` public aliases added. **123** total tests passing.

---

### Step 8 — Text integration harness (Iteration 0 + 15)
**Goal:** DSL runner matches spec exactly.

1. **`ScriptRunner`** supports only: `Board`, `click`, `wait`, `print board`.
2. Remove `jump` command handler.
3. Runner flow (no shortcuts):
   ```
   BoardParser → GameEngine
   click       → Controller.click
   wait        → GameEngine.wait
   print board → BoardPrinter.print(snapshot or board)
   ```
4. Add `tests/integration/scripts/` with `.kfc` files from spec (01–06).
5. Add `tests/integration/test_text_scripts.py` comparing `print board` output.

**Done when:** Integration scripts pass; runner never calls `Board.move_piece` directly.

**Status:** Complete — `ScriptRunner` routes `click` → `Controller.click`, `wait` → `GameEngine.wait`, `print board` → `BoardPrinter`; six `.kfc` scripts in `tests/integration/scripts/` with `tests/integration/test_text_scripts.py`. **123** total tests passing.

---

### Step 9 — Snapshot & renderer (Iteration 9)
**Goal:** Minimal playable UI on tested command path.

1. Define **`GameSnapshot`**: board size, pieces (kind/color/pixel pos/state), selected cell, `game_over`.
2. Implement **`GameEngine.snapshot() -> GameSnapshot`** (read-only).
3. Implement **`Renderer`**: grid, pieces, selection highlight, in-motion interpolation, game-over message.
4. **`app.py`**: UI clicks → `Controller.click`; draw loop reads snapshot only.
5. Smoke test: renderer does not mutate game state.

**Done when:** Minimal UI playable; renderer receives snapshot only.

**Status:** Complete — `GameSnapshot` / `PieceSnapshot` added with motion interpolation, `GameEngine.snapshot()` implemented; text `Renderer` formats snapshots (no Tkinter); `app.py` is a stdin text entry. Snapshot/renderer tests included.

---

### Step 10 — Test split & cleanup (Iteration 10)
**Goal:** Maintainable test layout matching spec.

1. Split `tests/unit/test_kfchess.py` into per-component files listed in spec §5.
2. Remove dead code: root duplicates, unused shims, `__pycache__` from VCS.
3. Refactor large classes if any exceed reasonable size.
4. Update `Architacture.md` to match final design.
5. Final regression: all unit + integration tests green.

**Done when:** Test layout matches spec; documentation current.

**Status:** Complete — `test_kfchess.py` split into `test_script_runner.py`, `test_game_engine_integration.py`, `test_pawn_movement.py`, `test_knight_movement.py`; validation tests merged into `test_board_parser.py`; `ChessGameSimulator` shim removed; dead stubs (`script_parser.py`, `image_view.py`) deleted; `Architacture.md` updated. **132** total tests passing.

---

## Features to Remove or Defer (extra route)

These exist in the current codebase but are **not** in the common route. Remove them during Steps 5–6, or isolate behind a feature flag if grader still needs them temporarily:

| Feature | Spec status |
|---------|-------------|
| Simultaneous multiple motions | Extra route |
| Opposite-color route delay / collision | Extra route |
| `jump` DSL command | Not in DSL |
| In-place airborne capture | Not in common route |
| Pawn two-step from start | **Contradicts** common route |
| Pawn promotion to queen | **Contradicts** common route |
| Premove redirect blocking | Extra route (collision) |

**Decision point:** If the course grader tests extra-route behavior, document which grader tests map to extra route and implement **one** extra feature cleanly after Step 10, per spec §3.

---

## Suggested Work Order (summary)

```
Step 0  Baseline
Step 1  Model (Piece, Board, Parser, Printer)
Step 2  Controller + BoardMapper
Step 3  PieceRules + RuleEngine API
Step 4  GameEngine.request_move + MoveResult
Step 5  RealTimeArbiter + single motion + timing
Step 6  Captures + game over + remove non-spec pawn/jump behavior
Step 7  Invalid moves + stable reasons
Step 8  ScriptRunner + integration .kfc scripts
Step 9  GameSnapshot + Renderer + app.py UI
Step 10 Test split + docs + cleanup
```

---

## Definition of Done (per spec §21)

A step is complete only when:
1. Unit tests cover the layer’s logic.
2. At least one `print board` integration test covers user-visible behavior (where applicable).
3. No UI dependency in the model.
4. Tests use `wait(ms)`, never real sleep.
5. Each changed class has a clear single responsibility.
6. All existing regression tests still pass (or failures are intentional spec alignments with updated expectations).

---

## Reference

- Course specification: `kung_fu_chess_en.docx`
- Condensed rules: `kungfu_chess/.cursorrules`
- Entry point: `main.py` → `p_input.py` → `kungfu_chess/texttests/script_runner.py`
