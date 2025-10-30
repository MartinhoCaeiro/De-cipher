def generate_normal_board(key):
    board = []
    letters = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    for char in key:
        if char not in letters:
            continue
        if char == 'I':
            if 'I/J' not in board:
                board.append('I/J')
        if char not in board:
            board.append(char)
    # Fill the remaining spaces with letters not in the key
    for char in letters:
        if char not in board:
            if char == 'I':
                board.append('I/J')
            else:
                board.append(char)
            
    # Create a 5x5 matrix
    return [board[i:i + 5] for i in range(0, 25, 5)]
def print_board(board):
    for row in board:
        print(' '.join(row))

def search_letter(board, letter):
    for i, row in enumerate(board):
        for j, char in enumerate(row):
            if char == letter or (char == 'I/J' and letter in 'IJ'):
                return (i, j)
    return None

def crypto_message(message, board):
    new_message = fix_message(message)
    pairs = [new_message[i:i+2] for i in range(0, len(new_message), 2)]
    print_board(board)
    for pair in pairs:
        print(pair)
        pair_coords = []
        for char in pair:
            pair_coords.append(search_letter(board, char))
            print(search_letter(board, char))
        if pair_coords[0][0] == pair_coords[1][0]:  # Same row
                print("Same row")
                board_row = board[pair_coords[0][0]]
    
                print(board_row)
        elif pair_coords[0][1] == pair_coords[1][1]:  # Same column
                print("Same column")
        else:  # Rectangle swap
                print("Rectangle swap")
    
def fix_message(message):
    i = 0
    for char in message:
        i = i + 1 

    for i in range(0, len(message), 2):
        if message[i] == message[i + 1]:
            message = message[:i + 1] + 'X' + message[i + 1:]
    if i % 2 != 0:
        message += 'X'
    return message
new_board = generate_normal_board("OLA")

crypto_message("HELLO", new_board)