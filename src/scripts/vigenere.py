# scripts/vigenere.py
import os

def read_table_from_file(path):
    """Lê a tabela de Vigenère (26x26) de um ficheiro de texto."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Ficheiro da tabela não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip().upper() for line in f if line.strip()]

    # Validar tabela 26x26
    if len(lines) != 26 or any(len(line) != 26 for line in lines):
        raise ValueError("A tabela Vigenère deve conter 26 linhas de 26 letras cada.")
    return lines


def read_key_from_file(path):
    """Lê a chave de um ficheiro de texto (apenas caracteres A–Z)."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Ficheiro da chave não encontrado: {path}")
    with open(path, "r", encoding="utf-8") as f:
        key = ''.join(ch for ch in f.read().upper() if ch.isalpha())
    if not key:
        raise ValueError("A chave Vigenère está vazia ou inválida.")
    return key


def encrypt_char(ch, key_ch, table):
    """Cifra um único carácter usando a tabela."""
    row = ord(key_ch) - ord('A')
    col = ord(ch) - ord('A')
    return table[row][col]


def decrypt_char(ch, key_ch, table):
    """Decifra um único carácter usando a tabela."""
    row = ord(key_ch) - ord('A')
    row_data = table[row]
    col = row_data.find(ch)
    if col == -1:
        return ch
    return chr(ord('A') + col)


def process_text(text, key, table, mode="encrypt"):
    """Cifra ou decifra texto ASCII visível com Vigenère."""
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


def encrypt_file(input_path, output_path, key=""):
    """Cifra um ficheiro de texto usando a tabela e a chave de ficheiros."""
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


def decrypt_file(input_path, output_path, key=""):
    """Decifra um ficheiro de texto usando a tabela e a chave de ficheiros."""
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
