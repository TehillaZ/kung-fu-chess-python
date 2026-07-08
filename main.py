import sys
from validate import validatefunc
from simulator import ChessGameSimulator

def process_vpl_input(raw_input_data: str):
    """Parses complete execution text payload separating metadata configurations."""
    
    output = validatefunc(raw_input_data)
    if output is not None:
       print(output)
       return
        
    board_lines = []
    command_lines = []
    is_command_block = False
    raw_lines = [
        line.strip()
        for line in raw_input_data.strip().split("\n")
        if line.strip()
    ]
    
    for line in raw_lines:
        # Filter metadata headers
        if line.startswith("Board:"):
            continue
        if line.startswith("Commands:"):
            is_command_block = True
            continue
            
        if is_command_block:
            command_lines.append(line)
        else:
            board_lines.append(line)

    # Build internal engine instance
    board_string = "\n".join(board_lines)
    simulator = ChessGameSimulator(board_string)

    # Action Processing Loop
    for command in command_lines:
        if command.startswith("click"):
            _, x_str, y_str = command.split()
            simulator.execute_click(int(x_str), int(y_str))
        elif command.startswith("wait"):
            _, ms_str = command.split()
            simulator.execute_wait(int(ms_str))
        elif command == "print board":
            simulator.print_board()

if __name__ == "__main__":
    # Read from stdin and process the input
    import sys
    input_data = sys.stdin.read()
    process_vpl_input(input_data)

