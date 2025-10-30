# scripts/playfair.py
import os

def read_board_from_file(path):
    """Lê a tabela Playfair (5x5) de um ficheiro de texto."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Ficheiro da tabela não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip().upper().replace("J", "I") for line in f if line.strip()]

    board = []
    for line in lines:
        for ch in line:
            if ch.isalpha() and ch not in [c for row in board for c in row]:
                if len(board) == 0 or len(board[-1]) == 5:
                    board.append([])
                if len(board[-1]) < 5:
                    board[-1].append(ch)

    # Flatten if needed (ensure exactly 5x5)
    flat = [c for row in board for c in row]
    if len(flat) < 25:
        for ch in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
            if ch not in flat:
                flat.append(ch)
            if len(flat) == 25:
                break
        board = [flat[i:i+5] for i in range(0, 25, 5)]

    return board



def search_letter(board, letter):
    """Procura uma letra na tabela."""
    letter = letter.upper().replace("J", "I")
    for i, row in enumerate(board):
        for j, char in enumerate(row):
            if char == letter:
                return (i, j)
    return None


def fix_message(message):
    """Prepara o texto (remove espaços, duplica letras iguais com X)."""
    message = ''.join(ch for ch in message.upper() if ch.isascii() and ch.isalpha())
    i = 0
    result = ""
    while i < len(message):
        a = message[i]
        b = message[i + 1] if i + 1 < len(message) else "X"
        if a == b:
            result += a + "X"
            i += 1
        else:
            result += a + b
            i += 2
    if len(result) % 2 != 0:
        result += "X"
    return result


def process_pair(board, a, b, mode="encrypt"):
    pos_a = search_letter(board, a)
    pos_b = search_letter(board, b)
    if not pos_a or not pos_b:
        return a + b

    if pos_a[0] == pos_b[0]:  # mesma linha
        if mode == "encrypt":
            return board[pos_a[0]][(pos_a[1] + 1) % 5] + board[pos_b[0]][(pos_b[1] + 1) % 5]
        else:
            return board[pos_a[0]][(pos_a[1] - 1) % 5] + board[pos_b[0]][(pos_b[1] - 1) % 5]

    elif pos_a[1] == pos_b[1]:  # mesma coluna
        if mode == "encrypt":
            return board[(pos_a[0] + 1) % 5][pos_a[1]] + board[(pos_b[0] + 1) % 5][pos_b[1]]
        else:
            return board[(pos_a[0] - 1) % 5][pos_a[1]] + board[(pos_b[0] - 1) % 5][pos_b[1]]

    else:  # retângulo
        return board[pos_a[0]][pos_b[1]] + board[pos_b[0]][pos_a[1]]


def encrypt_text(text, board):
    text = fix_message(text)
    result = ""
    for i in range(0, len(text), 2):
        result += process_pair(board, text[i], text[i + 1], "encrypt")
    return result


def decrypt_text(text, board):
    text = text.upper().replace(" ", "")
    result = ""
    for i in range(0, len(text), 2):
        result += process_pair(board, text[i], text[i + 1], "decrypt")
    return result


def encrypt_file(input_path, output_path, key=""):
    """Cifra um ficheiro de texto com Playfair, lendo a tabela de outro ficheiro."""
    board = read_board_from_file(key)
    with open(input_path, "r", encoding="utf-8") as f_in:
        text = f_in.read()
    cipher = encrypt_text(text, board)
    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write(cipher)


def decrypt_file(input_path, output_path, key=""):
    """Decifra um ficheiro de texto com Playfair, lendo a tabela de outro ficheiro."""
    board = read_board_from_file(key)
    with open(input_path, "r", encoding="utf-8") as f_in:
        text = f_in.read()
    plain = decrypt_text(text, board)
    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write(plain)
