"""Vigenère cipher helpers using a 95×95 table of visible ASCII chars.

This module operates with a 95×95 Vigenère table built from the visible
ASCII characters including space (code points 32..126). It provides
helpers to read a table file and a key file, build mappings, and
encrypt/decrypt text and files using the provided table and key.

The implementation validates the table file strictly: it expects
exactly 95 non-empty rows each containing exactly the 95 visible ASCII
characters (32..126) in some order.
"""

import os


def read_table_from_file(path: str):
    """Read a 95×95 Vigenère table from `path` and return list of rows.

    Behavior:
    - Reads non-empty lines from `path` and strips trailing newlines.
    - Validates there are exactly 95 rows and each row has length 95.
    - Validates the first row contains exactly the set of visible ASCII
      characters (code points 32..126) and that every subsequent row
      is a permutation of that set.

    Returns:
        list[str]: the table rows (95 strings of 95 characters).
    Raises:
        FileNotFoundError: if `path` does not exist.
        ValueError: on malformed or empty table files.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Tabela não encontrada: {path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n\r") for line in f if line.strip()]

    if not lines:
        raise ValueError("Tabela vazia.")

    n = len(lines)
    if n != 95:
        raise ValueError("A tabela deve ter 95 linhas (95×95 ASCII visíveis).")

    if any(len(row) != 95 for row in lines):
        raise ValueError("Todas as linhas devem ter exatamente 95 caracteres.")

    allowed = {chr(i) for i in range(32, 127)}
    first_row_set = set(lines[0])

    if first_row_set != allowed:
        raise ValueError("A primeira linha deve conter exatamente os ASCII visíveis (32..126) sem repetição.")

    for idx, row in enumerate(lines[1:], start=2):
        if set(row) != first_row_set:
            raise ValueError(f"Linha {idx} não contém os mesmos caracteres da primeira linha.")

    return lines


def read_key_from_file(path: str):
    """Read a key from `path` and return only visible ASCII characters.

    The function reads the file and returns a string containing only
    visible ASCII characters (code points 33..126) found in the file.

    Raises:
        FileNotFoundError: if `path` does not exist.
        ValueError: if the resulting key is empty (no visible ASCII chars).
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Chave não encontrada: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = f.read()

    allowed = {chr(i) for i in range(32, 127)}
    key = ''.join(ch for ch in data if ch in allowed)

    if not key:
        raise ValueError("A chave está vazia ou não contém ASCII visível.")

    return key


def build_mapping(table):
    """Build mapping helpers from `table`.

    Returns a tuple (charset, mapping, reverse) where:
    - `charset` is the ordered list of characters taken from first row.
    - `mapping` maps character -> column index.
    - `reverse` maps column index -> character.
    """
    charset = list(table[0])
    mapping = {c: i for i, c in enumerate(charset)}
    reverse = {i: c for i, c in enumerate(charset)}
    return charset, mapping, reverse


def encrypt_char(ch, kch, table, mapping):
    """Encrypt a single character `ch` using key character `kch`.

    If either `ch` or `kch` is not present in `mapping`, the original
    `ch` is returned unchanged (non-table characters are left alone).
    """
    if ch not in mapping or kch not in mapping:
        return ch
    row = mapping[kch]
    col = mapping[ch]
    return table[row][col]


def decrypt_char(ch, kch, table, mapping, reverse):
    """Decrypt a single character `ch` using key character `kch`.

    If `kch` is not in `mapping` or `ch` is not found in the selected
    row, the original `ch` is returned unchanged.
    """
    if kch not in mapping:
        return ch
    row = table[mapping[kch]]
    col = row.find(ch)
    if col == -1:
        return ch
    return reverse[col]


def vigenere(text, key, table, mode="encrypt"):
    """Apply the Vigenère cipher to `text` using `key` and `table`.

    The function:
    - builds charset/mappings from `table` (first row defines charset),
    - filters `text` to only characters present in the table charset,
    - repeats `key` as necessary and applies per-character encrypt or
      decrypt using `encrypt_char`/`decrypt_char`.

    `mode` may be "encrypt" or "decrypt".
    """
    charset, mapping, reverse = build_mapping(table)
    allowed = set(charset)

    text = ''.join(ch for ch in text if ch in allowed)

    res = []
    ki = 0

    for ch in text:
        kc = key[ki % len(key)]
        if mode == "encrypt":
            res.append(encrypt_char(ch, kc, table, mapping))
        else:
            res.append(decrypt_char(ch, kc, table, mapping, reverse))
        ki += 1

    return "".join(res)


def encrypt_file(input_path, output_path, key_paths):
    """Encrypt the file at `input_path` and write ciphertext to `output_path`.

    Parameters:
        input_path (str): path to the plaintext input file (UTF-8).
        output_path (str): path where ciphertext will be written (UTF-8).
        key_paths (tuple): tuple of two paths `(table_path, key_path)`.

    Behavior:
        - Reads the Vigenère table using `read_table_from_file` and the
          key using `read_key_from_file`.
        - Reads the entire input file as UTF-8, filters characters to the
          table charset, encrypts with `vigenere(..., mode="encrypt")`,
          and writes the resulting ciphertext as UTF-8 to `output_path`.

    Raises:
        FileNotFoundError: if either `table_path`, `key_path` or `input_path`
            does not exist.
        ValueError: if the table or key files are malformed.
    """
    table_path, key_path = key_paths
    table = read_table_from_file(table_path)
    key = read_key_from_file(key_path)

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    cipher = vigenere(text, key, table, "encrypt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cipher)


def decrypt_file(input_path, output_path, key_paths):
    """Decrypt the file at `input_path` and write plaintext to `output_path`.

    Parameters:
        input_path (str): path to the ciphertext input file (UTF-8).
        output_path (str): path where plaintext will be written (UTF-8).
        key_paths (tuple): tuple of two paths `(table_path, key_path)`.

    Behavior:
        - Reads the Vigenère table using `read_table_from_file` and the
          key using `read_key_from_file`.
        - Reads the entire input file as UTF-8, applies
          `vigenere(..., mode="decrypt")`, and writes the resulting
          plaintext as UTF-8 to `output_path`.

    Raises:
        FileNotFoundError: if either `table_path`, `key_path` or `input_path`
            does not exist.
        ValueError: if the table or key files are malformed.
    """
    table_path, key_path = key_paths
    table = read_table_from_file(table_path)
    key = read_key_from_file(key_path)

    with open(input_path, "r", encoding="utf-8") as f:
        cipher = f.read()

    text = vigenere(cipher, key, table, "decrypt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
