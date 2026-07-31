from server.room import Room


class RoomManager:
    """room_id -> Room registry. Creates the room (and its games row) on first join."""

    def __init__(self, board_string, repository=None):
        self._board_string = board_string
        self._repository = repository
        self._rooms = {}

    def get_or_create(self, room_id):
        room = self._rooms.get(room_id)
        if room is not None:
            return room

        room = Room(room_id, self._board_string, repository=self._repository)
        if self._repository is not None:
            game_id = self._repository.create_game(room_id, room.rows, room.cols)
            room.attach_game(game_id)

        self._rooms[room_id] = room
        return room

    def remove_if_empty(self, room_id):
        room = self._rooms.get(room_id)
        if room is not None and not room.connections():
            del self._rooms[room_id]

    def get(self, room_id):
        return self._rooms.get(room_id)
