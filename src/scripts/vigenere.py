"""Vigenère cipher helpers using a provided 26x26 table file.

This module reads a Vigenère table (26x26), a key file (A–Z), and
provides text and file-level encrypt/decrypt helpers. Text is normalized
to visible ASCII letters only before processing.
"""

import os


def read_table_from_file(path: str):
    """Read a 26x26 Vigenère table from `path`.

    The file must contain 26 lines of 26 letters each (A–Z). Returns a
    list of 26 strings representing the table rows.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Ficheiro da tabela não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip().upper() for line in f if line.strip()]

    if len(lines) != 26 or any(len(line) != 26 for line in lines):
        raise ValueError("A tabela Vigenère deve conter 26 linhas de 26 letras cada.")
    return lines


def read_key_from_file(path: str) -> str:
    """Read a Vigenère key from a file and return uppercase letters only.

    Raises FileNotFoundError if the file doesn't exist and ValueError if
    the resulting key is empty.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Ficheiro da chave não encontrado: {path}")
    with open(path, "r", encoding="utf-8") as f:
        key = ''.join(ch for ch in f.read().upper() if ch.isalpha())
    if not key:
        raise ValueError("A chave Vigenère está vazia ou inválida.")
    return key


def encrypt_char(ch: str, key_ch: str, table) -> str:
    """Encrypt a single uppercase character `ch` using table and key_ch."""
    row = ord(key_ch) - ord('A')
    col = ord(ch) - ord('A')
    return table[row][col]


def decrypt_char(ch: str, key_ch: str, table) -> str:
    """Decrypt a single character using the row determined by `key_ch`."""
    row = ord(key_ch) - ord('A')
    row_data = table[row]
    col = row_data.find(ch)
    if col == -1:
        return ch
    return chr(ord('A') + col)


def process_text(text: str, key: str, table, mode: str = "encrypt") -> str:
    """Encrypt or decrypt `text` using Vigenère with the provided table.

    The function normalizes `text` to upper-case ASCII letters before
    processing and advances the key index across letters only.
    """
    text = ''.join(ch for ch in text.upper() if ch.isascii() and ch.isalpha())
    result = ""
    key_index = 0
    for ch in text:
        key_ch = key[key_index % len(key)]
        if mode == "encrypt":
            result += encrypt_char(ch, key_ch, table)
        else:
            result += decrypt_char(ch, key_ch, table)
        key_index += 1
    return result


def encrypt_file(input_path: str, output_path: str, key=""):
    """Encrypt a text file using a Vigenère table and key file.

    The `key` parameter must be a sequence (list/tuple) of two paths:
    [table_path, key_path].
    """
    if not isinstance(key, (list, tuple)) or len(key) != 2:
        raise ValueError("O parâmetro 'key' deve ser uma lista/tuplo [tabela_path, chave_path].")

    table_path, key_path = key
    table = read_table_from_file(table_path)
    key_str = read_key_from_file(key_path)

    with open(input_path, "r", encoding="utf-8") as f_in:
        text = f_in.read()
    cipher = process_text(text, key_str, table, mode="encrypt")

    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write(cipher)


def decrypt_file(input_path: str, output_path: str, key=""):
    """Decrypt a Vigenère-encrypted text file using table and key files."""
    if not isinstance(key, (list, tuple)) or len(key) != 2:
        raise ValueError("O parâmetro 'key' deve ser uma lista/tuplo [tabela_path, chave_path].")

    table_path, key_path = key
    table = read_table_from_file(table_path)
    key_str = read_key_from_file(key_path)

    with open(input_path, "r", encoding="utf-8") as f_in:
        text = f_in.read()
    plain = process_text(text, key_str, table, mode="decrypt")

    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write(plain)
