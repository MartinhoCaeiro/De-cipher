"""Playfair cipher helpers and file interface.

This module implements a simple Playfair cipher with helpers to read a
5x5 board from a file, prepare messages, encrypt/decrypt digraphs,
and operate on files. All text is uppercased and the letter 'J' is
mapped to 'I' consistently by the implementation.
"""

import os


def read_board_from_file(path: str):
    """Read a Playfair 5x5 board from `path` and return it as a 5x5 list.

    Behavior details:
    - Lines in the file are scanned for letters; non-letter characters
      are ignored.
    - Any 'J' characters in the file are treated as 'I'.
    - Duplicate letters are skipped; if the supplied file does not
      contain 25 distinct cells, the remaining letters A..Z (with 'J'
      omitted) are appended in alphabetical order to fill a 5x5 board.

    Returns a list of 5 rows, each a list of 5 single-character strings.

    Raises:
        FileNotFoundError: if `path` does not exist.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Ficheiro da tabela não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        chars = []
        for line in f:
            for ch in line.strip().upper():
                if "A" <= ch <= "Z":
                    if ch == "J":
                        ch = "I"
                    if ch not in chars:
                        chars.append(ch)

    for c in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if c not in chars:
            chars.append(c)

    chars = chars[:25]
    return [chars[i:i+5] for i in range(0, 25, 5)]


def write_board_to_file(path: str, board, use_ij: bool = True):
    """Write a Playfair 5x5 `board` to `path`.

    Each row of the board is written on a separate line. When
    `use_ij` is True any cell equal to the single letter 'I' is written
    as the two-character sequence "I/J" so that the I/J convention is
    explicit in the saved file; other cells are written as their single
    letter. The function will create the target directory if necessary.
    """
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


def search_letter(board, letter):
    """Return the (row, col) position of `letter` in `board` or `None`.

    The search is case-insensitive; any input 'J' is treated as 'I'. If
    the letter is not present in `board` the function returns `None`.
    """
    letter = letter.upper()
    if letter == "J":
        letter = "I"
    for r, row in enumerate(board):
        for c, ch in enumerate(row):
            if ch == letter:
                return r, c
    return None


def fix_message(msg: str) -> str:
    """Normalize a message for Playfair and return an even-length string.

    Steps performed:
    - Convert to upper case and map 'J' to 'I'.
    - Drop any character outside 'A'..'Z'.
    - Split the cleaned text into digraphs. If a digraph contains two
      identical letters, insert 'X' between them and continue (the
      original repeated letter becomes the first letter of the next
      digraph).
    - If the final output has odd length, append a trailing 'X' to make
      the length even.
    """
    msg = msg.upper().replace("J", "I")
    msg = "".join(ch for ch in msg if "A" <= ch <= "Z")

    result = ""
    i = 0
    while i < len(msg):
        a = msg[i]
        b = msg[i + 1] if i + 1 < len(msg) else "X"
        if a == b:
            result += a + "X"
            i += 1
        else:
            result += a + b
            i += 2

    if len(result) % 2 == 1:
        result += "X"

    return result


def process_pair(board, a, b, decrypt=False):
    """Process a digraph (a, b) using Playfair rules and return two chars.

    The boolean parameter `decrypt` selects decryption behavior when
    True; otherwise encryption rules are applied. Both input letters
    are mapped so that 'J' is treated as 'I' during lookup. The function
    expects both letters to exist in `board`; if a letter is missing the
    call will raise an error when attempting to unpack the search result.
    """
    pos = search_letter(board, a)
    if pos is None:
        raise ValueError(f"Letter {a!r} not found in Playfair board")
    r1, c1 = pos

    pos = search_letter(board, b)
    if pos is None:
        raise ValueError(f"Letter {b!r} not found in Playfair board")
    r2, c2 = pos

    if r1 == r2:  
        if decrypt:
            return board[r1][(c1 - 1) % 5] + board[r2][(c2 - 1) % 5]
        else:
            return board[r1][(c1 + 1) % 5] + board[r2][(c2 + 1) % 5]

    if c1 == c2: 
        if decrypt:
            return board[(r1 - 1) % 5][c1] + board[(r2 - 1) % 5][c2]
        else:
            return board[(r1 + 1) % 5][c1] + board[(r2 + 1) % 5][c2]

    return board[r1][c2] + board[r2][c1]


def encrypt_text(text: str, board):
    """Encrypt `text` (string) using the provided Playfair `board`.

    The plaintext is first normalized with :func:`fix_message` to produce
    an even-length string of digraphs; each digraph is then transformed
    with :func:`process_pair`.
    """
    text = fix_message(text)
    result = ""
    for i in range(0, len(text), 2):
        result += process_pair(board, text[i], text[i+1])
    return result


def decrypt_text(text: str, board):
    """Decrypt `text` using the Playfair `board`.

    The input is uppercased, 'J' is mapped to 'I', and non-letter
    characters are removed. The function treats the cleaned input as a
    sequence of digraphs and applies `process_pair(..., decrypt=True)`
    to each digraph. Note: this routine does not try to remove padding
    characters (for example inserted 'X's).
    """
    text = text.upper().replace("J", "I")
    text = "".join(ch for ch in text if "A" <= ch <= "Z")
    result = ""
    for i in range(0, len(text), 2):
        result += process_pair(board, text[i], text[i+1], decrypt=True)
    return result


def encrypt_file(input_path: str, output_path: str, key: str):
    """Encrypt a text file using a Playfair board stored in `key`.

    Args:
        input_path: plaintext input file path.
        output_path: where the ciphertext will be written.
        key: path to the board file.
    """
    board = read_board_from_file(key)
    with open(input_path, "r", encoding="utf-8") as f:
        msg = f.read()
    cipher = encrypt_text(msg, board)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cipher)


def decrypt_file(input_path: str, output_path: str, key: str):
    """Decrypt a Playfair-encrypted text file using the given board.

    Args:
        input_path: encrypted input file path.
        output_path: where the decrypted plaintext will be written.
        key: path to the board file.
    """
    board = read_board_from_file(key)
    with open(input_path, "r", encoding="utf-8") as f:
        cipher = f.read()
    plain = decrypt_text(cipher, board)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(plain)
