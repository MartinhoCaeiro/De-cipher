"""Vigenère cipher helpers using a provided table file.

This module supports the classic 26x26 A–Z Vigenère table and an
extended table containing all visible ASCII characters (33..126),
i.e. a 94x94 table. The module reads a table file, a key file and
provides text and file-level encrypt/decrypt helpers. The behaviour
adapts depending on the table size:

- 26x26 : operates on uppercase A..Z (legacy behaviour)
- 94x94 : operates on visible ASCII characters (codes 33..126)
"""

import os


def read_table_from_file(path: str):
    """Read a Vigenère table from `path`.

    The file must contain N lines of N characters each (a square table).
    Rows must contain only visible ASCII characters (codes 33..126).
    The function validates that all rows have the same length and that
    the set of characters in each row matches the set in the first row.
    Returns a list of strings representing the table rows.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Ficheiro da tabela não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        # preserve character case for extended tables; caller will
        # interpret characters based on table size.
        lines = [line.rstrip("\n\r") for line in f if line.strip()]

    if not lines:
        raise ValueError("A tabela Vigenère está vazia.")

    n = len(lines)
    row_len = len(lines[0])
    if any(len(line) != row_len for line in lines):
        raise ValueError("A tabela Vigenère deve ser quadrada (todas as linhas do mesmo comprimento).")
    if n != row_len:
        raise ValueError("A tabela Vigenère deve ser quadrada (N x N).")

    # Validate characters: only visible ASCII allowed; include space (32..126)
    visible = {chr(i) for i in range(32, 127)}
    first_set = set(lines[0])
    if not first_set.issubset(visible):
        raise ValueError("A tabela contém caracteres não visíveis ASCII (somente 32..126 são suportados).")

    # Ensure each row uses the same set of characters as the first row
    for idx, row in enumerate(lines[1:], start=2):
        if set(row) != first_set:
            raise ValueError(f"A linha {idx} da tabela não contém o mesmo conjunto de caracteres da primeira linha.")

    # Ensure first row has unique characters (no duplicates)
    if len(first_set) != row_len:
        raise ValueError("A primeira linha da tabela contém caracteres duplicados; cada caractere deve aparecer exatamente uma vez.")

    return [line for line in lines]


def read_key_from_file(path: str, allowed_chars: set = None) -> str:
    """Read a Vigenère key from `path` and return characters filtered by allowed_chars.

    If `allowed_chars` is None the function returns visible ASCII
    characters (33..126) found in the key file. If provided, only
    characters present in `allowed_chars` are kept. Raises
    FileNotFoundError or ValueError on problems.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Ficheiro da chave não encontrado: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    if allowed_chars is None:
        # default allowed includes space (32) through 126
        allowed_chars = {chr(i) for i in range(32, 127)}
    key = ''.join(ch for ch in data if ch in allowed_chars)
    if not key:
        raise ValueError("A chave Vigenère está vazia ou inválida para a tabela fornecida.")
    return key


def encrypt_char(ch: str, key_ch: str, table, mapping) -> str:
    """Encrypt a single character `ch` using `table` and `mapping`.

    `mapping` is a dict char->index for the table's charset. If a
    character is not present in `mapping` the function returns the
    character unchanged.
    """
    if key_ch not in mapping or ch not in mapping:
        return ch
    row = mapping[key_ch]
    col = mapping[ch]
    return table[row][col]


def decrypt_char(ch: str, key_ch: str, table, mapping, rev_mapping) -> str:
    """Decrypt a single character using `table` row defined by `key_ch`.

    `mapping` maps char->index and `rev_mapping` maps index->char for the
    table charset. If `ch` is not present in the row the function returns
    `ch` unchanged.
    """
    if key_ch not in mapping:
        return ch
    row = mapping[key_ch]
    row_data = table[row]
    col = row_data.find(ch)
    if col == -1:
        return ch
    return rev_mapping[col]


def _build_charset_and_mappings(table):
    # Derive charset from the first row of the table. The table must be
    # validated earlier to ensure the first row contains unique visible
    # ASCII characters and all rows share the same set.
    charset = list(table[0])
    mapping = {c: i for i, c in enumerate(charset)}
    rev_mapping = {i: c for i, c in enumerate(charset)}
    return charset, mapping, rev_mapping


def process_text(text: str, key: str, table, mode: str = "encrypt") -> str:
    """Encrypt or decrypt `text` using Vigenère with the provided table.

    The function adapts normalization depending on the table size: for a
    26x26 table it uppercases and keeps A..Z; for a 94x94 table it keeps
    visible ASCII characters (33..126) as-is.
    """
    charset, mapping, rev_mapping = _build_charset_and_mappings(table)

    allowed = set(charset)
    # Normalize text according to allowed charset. If charset contains
    # alphabetic uppercase letters only, perform uppercasing; otherwise
    # keep characters as-is (suitable for visible ASCII tables).
    if all('A' <= c <= 'Z' for c in charset):
        text = ''.join(ch for ch in text.upper() if ch in allowed)
    else:
        text = ''.join(ch for ch in text if ch in allowed)

    result = ""
    key_index = 0
    for ch in text:
        key_ch = key[key_index % len(key)]
        if mode == "encrypt":
            result += encrypt_char(ch, key_ch, table, mapping)
        else:
            result += decrypt_char(ch, key_ch, table, mapping, rev_mapping)
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
    # Derive allowed charset from the table
    charset, _, _ = _build_charset_and_mappings(table)
    allowed = set(charset)
    key_str = read_key_from_file(key_path, allowed_chars=allowed)

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
    charset, _, _ = _build_charset_and_mappings(table)
    allowed = set(charset)
    key_str = read_key_from_file(key_path, allowed_chars=allowed)

    with open(input_path, "r", encoding="utf-8") as f_in:
        text = f_in.read()
    plain = process_text(text, key_str, table, mode="decrypt")

    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write(plain)
