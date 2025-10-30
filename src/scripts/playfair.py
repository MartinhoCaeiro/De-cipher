def generate_normal_board(key):
    board = []
    letters = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # note: no J
    key_norm = ''.join([c for c in key.upper() if c.isalpha()])
    key_norm = key_norm.replace('J', 'I')

    for char in key_norm:
        if char == 'I':
            if 'I/J' not in board:
                board.append('I/J')
            continue
        if char not in board:
            board.append(char)

    for char in letters:
        if char == 'I':
            if 'I/J' not in board:
                board.append('I/J')
            continue
        if char not in board:
            board.append(char)

    # Cria o tabuleiro 5x5
    return [board[i:i + 5] for i in range(0, 25, 5)]


def print_board(board):
    for row in board:
        print(' '.join(row))


def search_letter(board, letter):
    if not letter or not letter.isalpha():
        return None
    letter = letter.upper()
    if letter == 'J':
        letter = 'I'
    for i, row in enumerate(board):
        for j, char in enumerate(row):
            if char == 'I/J' and letter in ('I', 'J'):
                return (i, j)
            if char == letter:
                return (i, j)
    return None


def _board_char(board, i, j):
    v = board[i][j]
    return 'I' if v == 'I/J' else v


def fix_message(message):
    msg = ''.join([c for c in message.upper() if c.isalpha()])
    msg = msg.replace('J', 'I')

    digrams = []
    i = 0
    while i < len(msg):
        a = msg[i]
        if i + 1 >= len(msg):
            b = 'X'
            i += 1
        else:
            b = msg[i + 1]
            if a == b:
                b = 'X'
                i += 1  
            else:
                i += 2
        digrams.append(a + b)
    return digrams


def crypto_message(message, board):
    digrams = fix_message(message)
    ciphertext = []

    for pair in digrams:
        a, b = pair[0], pair[1]
        pa = search_letter(board, a)
        pb = search_letter(board, b)
        if pa is None or pb is None:
            continue

        if pa[0] == pb[0]:
            row = pa[0]
            ca = _board_char(board, row, (pa[1] + 1) % 5)
            cb = _board_char(board, row, (pb[1] + 1) % 5)
            ciphertext.append(ca + cb)
        elif pa[1] == pb[1]:
            col = pa[1]
            ca = _board_char(board, (pa[0] + 1) % 5, col)
            cb = _board_char(board, (pb[0] + 1) % 5, col)
            ciphertext.append(ca + cb)
        else:
            ca = _board_char(board, pa[0], pb[1])
            cb = _board_char(board, pb[0], pa[1])
            ciphertext.append(ca + cb)

    result = ''.join(ciphertext)
    print(result)
    return result


if __name__ == '__main__':
    new_board = generate_normal_board("OLA")
    print_board(new_board)
    crypto_message("HELLO", new_board)