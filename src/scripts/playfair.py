"""Playfair cipher helpers and file interface.

This module implements a simple Playfair cipher with helpers to read a
5x5 board from a file, prepare messages, encrypt/decrypt text pairs,
and operate on files. The implementation uses the common convention of
merging 'J' into 'I'.
"""

import os
from typing import Optional, Set


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
        # Read non-empty lines (preserve original characters). We'll
        # interpret the file either as a classical 5x5 A..Z board or an
        # extended/custom board containing arbitrary visible ASCII.
        raw_lines = [line.rstrip("\n") for line in f if line.strip()]
        # Remove BOM if present in first line
        if raw_lines and raw_lines[0].startswith('\ufeff'):
            raw_lines[0] = raw_lines[0].lstrip('\ufeff')
        # For processing, strip surrounding whitespace but keep internal
        # characters (including punctuation and digits).
        lines = [line.strip() for line in raw_lines]

    # Collect characters preserving order, ignoring whitespace. We'll
    # keep duplicates out so the first occurrence determines placement.
    seen = []
    for line in lines:
        for ch in line:
            # For extended/custom boards we want to allow space and other
            # visible whitespace characters as valid board cells. Do not
            # skip whitespace here; keep the character as-is so files
            # that include a space in the table (e.g. the 10x10 sample)
            # will include it in the board.
            if ch not in seen:
                seen.append(ch)

    # Determine whether the provided board is a standard 5x5 A..Z board.
    # Criteria: all characters are letters A..Z or a..z and there are at
    # most 25 unique letter characters. In that case we normalize to the
    # classic uppercase A..Z without J (map J->I) behavior.
    letters_only = all(("A" <= c <= "Z") or ("a" <= c <= "z") for c in seen)
    if letters_only:
        # Build legacy 5x5 board: uppercase, map J->I, and keep A..Z only
        flat = []
        for ch in seen:
            ch2 = ch.upper().replace("J", "I")
            if "A" <= ch2 <= "Z" and ch2 not in flat:
                flat.append(ch2)
        # Fill with remaining alphabet (without J)
        for ch in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
            if ch not in flat:
                flat.append(ch)
            if len(flat) >= 25:
                break
        flat = flat[:25]
        board = [flat[i:i+5] for i in range(0, 25, 5)]
        return board

    # Otherwise treat the file as an extended/custom board. We'll build a
    # square board (N x N) from the unique characters provided. If the
    # provided characters don't form a perfect square we'll choose the
    # smallest N such that N*N >= len(flat) and fill remaining slots
    # with visible ASCII characters (33..125) not already used.
    flat = list(seen)
    if not flat:
        raise ValueError("Provided board file contains no usable characters")

    # Determine smallest square size that fits the provided characters
    import math
    n = int(math.ceil(math.sqrt(len(flat))))

    # Fill remaining slots up to n*n with visible ASCII characters
    for code in range(33, 126):
        if len(flat) >= n * n:
            break
        ch = chr(code)
        if ch not in flat:
            flat.append(ch)

    # If still not enough (very unlikely), expand n until we can fill
    while len(flat) > n * n:
        n += 1
        for code in range(33, 126):
            if len(flat) >= n * n:
                break
            ch = chr(code)
            if ch not in flat:
                flat.append(ch)

    flat = flat[: n * n]
    board = [flat[i:i + n] for i in range(0, n * n, n)]
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
    # Decide whether this is the classical board (5x5 uppercase letters)
    flat = [c for row in board for c in row]
    is_classic = len(flat) == 25 and all("A" <= c <= "Z" for c in flat)

    if is_classic:
        # For the classical board do case-insensitive lookup and map J->I
        letter = letter.upper().replace("J", "I")
    # Otherwise keep letter as provided (extended boards may be case-
    # sensitive and contain punctuation/digits).

    for i, row in enumerate(board):
        for j, char in enumerate(row):
            if char == letter:
                return (i, j)
    return None


def fix_message(message: str, allowed_chars: Optional[Set[str]] = None, map_j: bool = True) -> str:
    """Normalize a message for Playfair.

    Only ASCII letters A..Z are retained (J mapped to I). Other characters
    (digits, punctuation, accented letters, etc.) are removed. The result
    is uppercased. Repeated characters in a digraph are split with 'X' and
    the output is padded to even length with 'X'.
    """
    if allowed_chars is None:
        # Default behavior: classical Playfair with A..Z and J->I mapping
        message = ''.join(ch for ch in message.upper().replace("J", "I") if "A" <= ch <= "Z")
    else:
        # Keep only characters present in allowed_chars. Do not change
        # case or map J->I unless explicitly requested via map_j.
        s = message
        if map_j:
            s = s.replace("J", "I")
        # If we're using the classic mapping (map_j=True) the board
        # characters are uppercase A..Z. Uppercase the input so lowercase
        # letters are preserved when filtering against allowed_chars.
        if map_j:
            s = s.upper()
        message = ''.join(ch for ch in s if ch in allowed_chars)
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

    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0

    # Same row: move right (encrypt) or left (decrypt), wrapping by columns
    if pos_a[0] == pos_b[0]:
        if mode == "encrypt":
            return board[pos_a[0]][(pos_a[1] + 1) % cols] + board[pos_b[0]][(pos_b[1] + 1) % cols]
        else:
            return board[pos_a[0]][(pos_a[1] - 1) % cols] + board[pos_b[0]][(pos_b[1] - 1) % cols]

    # Same column: move down (encrypt) or up (decrypt), wrapping by rows
    elif pos_a[1] == pos_b[1]:
        if mode == "encrypt":
            return board[(pos_a[0] + 1) % rows][pos_a[1]] + board[(pos_b[0] + 1) % rows][pos_b[1]]
        else:
            return board[(pos_a[0] - 1) % rows][pos_a[1]] + board[(pos_b[0] - 1) % rows][pos_b[1]]

    else:
        return board[pos_a[0]][pos_b[1]] + board[pos_b[0]][pos_a[1]]


def encrypt_text(text: str, board) -> str:
    """Encrypt `text` (string) using the provided Playfair `board`.

    The text is normalized with :func:`fix_message` before processing.
    """
    # Derive allowed characters from the board. For the classic 5x5 board
    # this will be A..Z with J->I mapping; for extended boards we use the
    # exact characters that appear in the board.
    flat = [c for row in board for c in row]
    is_classic = len(flat) == 25 and all("A" <= c <= "Z" for c in flat)
    allowed = set(flat)
    text = fix_message(text, allowed_chars=allowed, map_j=is_classic)
    result = ""
    for i in range(0, len(text), 2):
        result += process_pair(board, text[i], text[i + 1], "encrypt")
    return result


def decrypt_text(text: str, board) -> str:
    """Decrypt `text` using the Playfair `board`.

    The function assumes input is already formatted as digraphs.
    """
    # Normalize input by keeping only characters that appear in the board.
    flat = [c for row in board for c in row]
    is_classic = len(flat) == 25 and all("A" <= c <= "Z" for c in flat)
    if is_classic:
        text = ''.join(ch for ch in text.upper().replace("J", "I") if ch in flat)
    else:
        text = ''.join(ch for ch in text if ch in flat)
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
    # When saving decrypted text, for the classical 5x5 alphabet board we
    # make the I/J convention explicit by writing I as I/J. For extended
    # boards we preserve characters as-is.
    flat = [c for row in board for c in row]
    is_classic = len(flat) == 25 and all(("A" <= c <= "Z") or ("a" <= c <= "z") for c in flat)
    if is_classic:
        out_text = plain.replace("I", "I/J")
    else:
        out_text = plain
    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write(out_text)
