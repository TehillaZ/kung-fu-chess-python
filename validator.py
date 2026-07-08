valid_tokens = {
        ".", 
        "wK", "wQ", "wR", "wB", "wN", "wP", 
        "bK", "bQ", "bR", "bB", "bN", "bP"
    }
    
def validatefunc(program_input:str):
    program_input = program_input.splitlines()

    board_lines = []
    inside_board = False
    
    for line in program_input:
        cleaned_line = line.strip()
        
        if cleaned_line.startswith("Commands:"):
            inside_board = False
            continue
            
        if inside_board and cleaned_line:
            board_lines.append(cleaned_line)
            
        if cleaned_line.startswith("Board:"):
            inside_board = True

    if not board_lines:
       return "ERROR EMPTY_BOARD"
    num_of_cols = len(board_lines[0].split())
    
    for line in board_lines:
        if len(line.split()) != num_of_cols:
            return "ERROR ROW_WIDTH_MISMATCH"
            
    
    
    for line in board_lines:
        tokens = line.split()
        for token in tokens:
            if token not in valid_tokens:
               return "ERROR UNKNOWN_TOKEN"
                
        
    return None