# simulator.py
import json
import os
KING = 'K'
ROOK = 'R'
BISHOP = 'B'
QUEEN = 'Q'
KNIGHT = 'N'
EMPTY_CELL = '.'

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'rules.json')

try:
    with open(CONFIG_PATH, 'r') as file:
        RULES = json.load(file)
except FileNotFoundError:
        RULES = {}

class ChessGameSimulator:
    def __init__(self, board_setup):
        
        self.board = [row.split() for row in board_setup.strip().split('\n')]
        self.selected_pos = None  
        self.clock = 0

    def _get_cell_coords(self, x: int, y: int):
        col = x // 100
        row = y // 100
        if 0 <= row < len(self.board) and 0 <= col < len(self.board[0]):
            return row, col
        return None

    def _is_legal_move(self, piece: str, start: tuple, end: tuple) -> bool:
        """Checks if a move is legal based on the dynamic JSON configuration."""
        if start == end:
            return False
            
        start_row, start_col = start
        end_row, end_col = end
        
        delta_row = abs(end_row - start_row)
        delta_col = abs(end_col - start_col)
        
        piece_type = piece[1] if len(piece) == 2 else piece
        
        custom_rules = RULES.get(piece_type)
        if not custom_rules:
            return True
            
        if "max_steps" in custom_rules:
            if delta_row > custom_rules["max_steps"] or delta_col > custom_rules["max_steps"]:
                return False
                
        if custom_rules.get("is_knight"):
            return (delta_row == 2 and delta_col == 1) or (delta_row == 1 and delta_col == 2)
            
        if delta_row == delta_col:
            return custom_rules.get("diagonal", False)
            
        if delta_row == 0 or delta_col == 0:
            return custom_rules.get("straight", False)
            
        return False
        
       

    def execute_click(self, x: int, y: int):
        coords = self._get_cell_coords(x, y)
        if not coords:
            return 
        
        row, col = coords
        cell_content = self.board[row][col]

        if self.selected_pos is None:
            if cell_content != EMPTY_CELL:
                self.selected_pos = (row, col)
        else:
            prev_row, prev_col = self.selected_pos
            piece = self.board[prev_row][prev_col]
            
            if cell_content != EMPTY_CELL:
                self.selected_pos = (row, col)
            else:
                if self._is_legal_move(piece, (prev_row, prev_col), (row, col)):
                    self.board[row][col] = piece
                    self.board[prev_row][prev_col] = EMPTY_CELL
                self.selected_pos = None  

    def execute_wait(self, ms: int):
        self.clock += ms

    def print_board(self):
        for row in self.board:
            print(" ".join(row))