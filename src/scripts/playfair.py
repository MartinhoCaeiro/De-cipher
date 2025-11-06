"""Playfair cipher helpers and file interface.

This module implements a simple Playfair cipher with helpers to read a
5x5 board from a file, prepare messages, encrypt/decrypt text pairs,
and operate on files. The implementation uses the common convention of
merging 'J' into 'I'.
"""

import os


def read_board_from_file(path: str):
    """Read a Playfair 5x5 board from `path` and return it as a list of lists.

    The file may contain rows of letters; non-letter characters are
    ignored. 'J' characters are treated as 'I'. If the provided board
    is incomplete, the remaining letters A..Z (without J) are filled in.

    Raises:
        FileNotFoundError: if the path does not exist.
    """
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

    # Flatten collected letters. Ensure we always return a 5x5 board:
    # - If fewer than 25 letters were provided, fill the remainder with
    #   the remaining alphabet (without J).
    # - If more than 25 letters were provided, ignore extras and truncate
    #   to the first 25 unique letters encountered.
    flat = [c for row in board for c in row]
    if len(flat) < 25:
        for ch in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
            if ch not in flat:
                flat.append(ch)
            if len(flat) == 25:
                break
    elif len(flat) > 25:
        flat = flat[:25]

    board = [flat[i:i+5] for i in range(0, 25, 5)]

    return board


def write_board_to_file(path: str, board, use_ij: bool = True):
    """Write a Playfair 5x5 `board` to `path`.

    If `use_ij` is True, cells that contain 'I' will be written as the
    two-character sequence "I/J" to make the I/J convention explicit in
    the saved file. Other cells are written as their single-letter
    representation. Each board row is written on its own line.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in board:
            out_cells = []
            for ch in row:
                if use_ij and str(ch).upper() == "I":
                    out_cells.append("I/J")
                else:
                    out_cells.append(str(ch))
            f.write("".join(out_cells) + "\n")


def search_letter(board, letter: str):
    """Return (row, col) of `letter` in `board`, or None if not found.

    Letter 'J' is mapped to 'I' and search is case-insensitive.
    """
    letter = letter.upper().replace("J", "I")
    for i, row in enumerate(board):
        for j, char in enumerate(row):
            if char == letter:
                return (i, j)
    return None


def fix_message(message: str) -> str:
    """Normalize a message for Playfair.

    Behaviour changed: accept all visible ASCII characters with codes
    from 33 to 125 (inclusive). Characters outside that range are removed.

    The function still uppercases the message (so letters become A..Z).
    Repeated characters are split with 'X' and the result is padded to
    even length with 'X' as before.
    """
    # Accept visible ASCII in the requested range (33..125). We uppercase
    # the input so letters are normalized; non-letter symbols remain as-is
    # if they are in the allowed ASCII range.
    message = ''.join(ch for ch in message.upper() if 33 <= ord(ch) <= 125)
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


def process_pair(board, a: str, b: str, mode: str = "encrypt") -> str:
    """Process a digraph (a,b) according to Playfair rules.

    Returns the transformed pair as a two-character string. Mode may be
    "encrypt" or "decrypt".
    """
    pos_a = search_letter(board, a)
    pos_b = search_letter(board, b)
    if not pos_a or not pos_b:
        return a + b

    if pos_a[0] == pos_b[0]:
        if mode == "encrypt":
            return board[pos_a[0]][(pos_a[1] + 1) % 5] + board[pos_b[0]][(pos_b[1] + 1) % 5]
        else:
            return board[pos_a[0]][(pos_a[1] - 1) % 5] + board[pos_b[0]][(pos_b[1] - 1) % 5]

    elif pos_a[1] == pos_b[1]:
        if mode == "encrypt":
            return board[(pos_a[0] + 1) % 5][pos_a[1]] + board[(pos_b[0] + 1) % 5][pos_b[1]]
        else:
            return board[(pos_a[0] - 1) % 5][pos_a[1]] + board[(pos_b[0] - 1) % 5][pos_b[1]]

    else:
        return board[pos_a[0]][pos_b[1]] + board[pos_b[0]][pos_a[1]]


def encrypt_text(text: str, board) -> str:
    """Encrypt `text` (string) using the provided Playfair `board`.

    The text is normalized with :func:`fix_message` before processing.
    """
    text = fix_message(text)
    result = ""
    for i in range(0, len(text), 2):
        result += process_pair(board, text[i], text[i + 1], "encrypt")
    return result


def decrypt_text(text: str, board) -> str:
    """Decrypt `text` using the Playfair `board`.

    The function assumes input is already formatted as digraphs.
    """
    text = text.upper().replace(" ", "")
    result = ""
    for i in range(0, len(text), 2):
        result += process_pair(board, text[i], text[i + 1], "decrypt")
    return result


def encrypt_file(input_path: str, output_path: str, key: str = ""):
    """Encrypt a text file using a Playfair board stored in `key`.

    Args:
        input_path: plaintext input file path.
        output_path: where the ciphertext will be written.
        key: path to the board file.
    """
    board = read_board_from_file(key)
    with open(input_path, "r", encoding="utf-8") as f_in:
        text = f_in.read()
    cipher = encrypt_text(text, board)
    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write(cipher)


def decrypt_file(input_path: str, output_path: str, key: str = ""):
    """Decrypt a Playfair-encrypted text file using the given board.

    Args:
        input_path: encrypted input file path.
        output_path: where the decrypted plaintext will be written.
        key: path to the board file.
    """
    board = read_board_from_file(key)
    with open(input_path, "r", encoding="utf-8") as f_in:
        text = f_in.read()
    plain = decrypt_text(text, board)
    # When saving decrypted text, write 'I' as 'I/J' so the I/J convention
    # is explicit in the output file (matches write_board_to_file behaviour).
    out_text = plain.replace("I", "I/J")
    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write(out_text)
