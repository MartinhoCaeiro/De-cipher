# scripts/des.py
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
import os

def _read_key_file(key_path: str) -> bytes:
    """Lê a chave de um ficheiro de texto (como string hexadecimal ou bytes)."""
    with open(key_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    try:
        key = bytes.fromhex(content)
    except ValueError:
        key = content.encode("utf-8")
    if len(key) != 8:
        raise ValueError("A chave DES deve ter exatamente 8 bytes (64 bits).")
    return key


def encrypt_file(input_path: str, output_path: str, key: str = ""):
    """Cifra um ficheiro com DES (modo CBC)."""
    if not os.path.isfile(key):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key}")
    key_bytes = _read_key_file(key)

    cipher = DES.new(key_bytes, DES.MODE_CBC)
    iv = cipher.iv

    with open(input_path, "rb") as f_in:
        data = f_in.read()

    # Padding (PKCS7)
    pad_len = DES.block_size - (len(data) % DES.block_size)
    data += bytes([pad_len]) * pad_len

    ciphertext = cipher.encrypt(data)

    with open(output_path, "wb") as f_out:
        f_out.write(iv + ciphertext)


def decrypt_file(input_path: str, output_path: str, key: str = ""):
    """Decifra um ficheiro cifrado com DES (modo CBC)."""
    if not os.path.isfile(key):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key}")
    key_bytes = _read_key_file(key)

    with open(input_path, "rb") as f_in:
        iv = f_in.read(8)
        ciphertext = f_in.read()

    cipher = DES.new(key_bytes, DES.MODE_CBC, iv=iv)
    data = cipher.decrypt(ciphertext)

    # Remove padding
    pad_len = data[-1]
    if pad_len < 1 or pad_len > DES.block_size:
        raise ValueError("Padding inválido ou chave incorreta.")
    data = data[:-pad_len]

    with open(output_path, "wb") as f_out:
        f_out.write(data)
