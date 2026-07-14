# Step 0 — Baseline & Inventory

Recorded: 2026-07-13

## Regression baseline

| Metric | Value |
|--------|-------|
| Unit tests | **132 passing** (134 before deduping 2 duplicate validation tests) |
| Command | `py -m unittest discover -s tests -p "test_*.py" -v` |
| Entry point | `main.py` → `p_input.py` → `ScriptRunner` |

## Target

Align implementation with the **common route** in `kung_fu_chess_en.docx` (see `PLAN.md`).

## Gaps vs common route

| # | Area | Current behavior | Spec requirement | Planned step |
|---|------|------------------|------------------|--------------|
| 1 | Motion policy | ~~Multiple simultaneous pending motions~~ | One active motion; `"motion_in_progress"` | **Step 5 (done)** |
| 2 | GameEngine API | ~~`execute_click` / `execute_wait`~~ | `request_move` → `MoveResult` | **Step 4 (done)** |
| 3 | Validation | ~~Loose string reasons~~ | `MoveValidation` with stable reasons | **Step 3–4 (done)** |
| 4 | Pawn | Two-step start + promotion | No two-step, no promotion | Step 6 |
| 5 | DSL | ~~`jump` command~~ | Only `Board`, `click`, `wait`, `print board` | **Step 6/8 (handler removed)** |
| 6 | Knight | ~~Airborne / in-place jump capture~~ | L-shaped move only | **Step 6 (done)** |
| 7 | Motion ownership | ~~`Controller.pending_motions`~~ | `RealTimeArbiter` owns motions | **Step 5 (done)** |
| 8 | Model | ~~String grid only~~ | `Piece` objects with id/cell/state | **Step 1 (done)** |
| 9 | PieceRules API | ~~`is_legal_move` validators~~ | `legal_destinations` set | **Step 3 (done)** |
| 10 | UI | ~~Renderer stub~~ | `GameSnapshot` + renderer | **Step 9 (done)** |
| 11 | Tests | Per-component unit + integration scripts | **Step 10 (done)** |
| 12 | Route conflicts | ~~Opposite-color delay / collision~~ | Not in common route | **Step 5 (removed)** |

## Features to remove or defer (extra route)

These exist today but are **not** in the common route. Do not extend them; remove during Steps 5–8 unless a grader test still requires them temporarily.

- [x] Simultaneous movement of multiple pieces (rejected via `motion_in_progress`)
- [x] Opposite-color common-route delay (`has_common_route` scheduling)
- [ ] Destination collision / first-arrival-wins
- [x] `jump` DSL command and in-place airborne capture
- [x] Knight airborne capture on enemy arrival
- [ ] Pawn two-step from start rank
- [ ] Pawn promotion to queen
- [ ] Premove redirect blocking while moving

## Grader-sensitive tests (keep working until aligned)

| Test | Notes |
|------|-------|
| `airborne_piece_captures_arriving_enemy` | Uses `jump` DSL — extra-route; remove in Step 8 unless grader requires |
| Advanced realtime interaction tests | Simultaneous motion — extra-route |
| Pawn promotion / two-step tests | Contradict common route — update in Step 6 |

## Compatibility shims (removed in Step 10)

- ~~`ChessGameSimulator`~~ — tests use `GameEngine` directly
- `Board.get_piece()` returning token strings — keep until upper layers use `piece_at()`
- `parse_board_and_commands()` — keep alongside `BoardParser.parse()`

## Step 0 status

- [x] Baseline test count recorded
- [x] Gaps documented
- [x] Extra-route features marked for removal
- [x] `ChessGameSimulator` removed; tests use `GameEngine`
