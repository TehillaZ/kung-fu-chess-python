import json

MESSAGE_TYPE_MOVE = "move"
MESSAGE_TYPE_ROLE = "role"
MESSAGE_TYPE_SNAPSHOT = "snapshot"
MESSAGE_TYPE_ERROR = "error"


class ProtocolError(ValueError):
    """Raised for malformed client messages."""


def decode_client_message(raw):
    try:
        payload = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ProtocolError(f"invalid_json: {exc}") from exc

    if not isinstance(payload, dict):
        raise ProtocolError("message_not_object")

    if payload.get("type") != MESSAGE_TYPE_MOVE:
        raise ProtocolError("unknown_message_type")

    source = _decode_cell(payload.get("from"))
    dest = _decode_cell(payload.get("to"))
    return {"type": MESSAGE_TYPE_MOVE, "from": source, "to": dest}


def _decode_cell(cell):
    if (
        not isinstance(cell, (list, tuple))
        or len(cell) != 2
        or not all(isinstance(value, int) for value in cell)
    ):
        raise ProtocolError("invalid_cell")
    return (cell[0], cell[1])


def encode_role(role):
    return {"type": MESSAGE_TYPE_ROLE, "role": role}


def encode_error(reason):
    return {"type": MESSAGE_TYPE_ERROR, "reason": reason}


def encode_snapshot(snapshot):
    return {
        "type": MESSAGE_TYPE_SNAPSHOT,
        "rows": snapshot.rows,
        "cols": snapshot.cols,
        "cell_size": snapshot.cell_size,
        "clock": snapshot.clock,
        "game_over": snapshot.game_over,
        "pieces": [_encode_piece(piece) for piece in snapshot.pieces],
    }


def _encode_piece(piece):
    return {
        "id": piece.piece_id,
        "color": piece.color,
        "kind": piece.kind,
        "row": piece.logical_row,
        "col": piece.logical_col,
        "pixel_x": piece.pixel_x,
        "pixel_y": piece.pixel_y,
        "state": piece.state,
        "sprite_state": piece.sprite_state,
        "animation_progress": piece.animation_progress,
    }
