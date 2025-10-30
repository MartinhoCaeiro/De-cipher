"""AES file encrypt/decrypt helpers (CBC mode).

This module provides a minimal helper API to encrypt and decrypt files
using AES in CBC mode. The key is loaded from a file which may contain
either a hex string or raw UTF-8 text. The encrypted output format is:

    IV (16 bytes) || ciphertext

Functions:
    - encrypt_file(input_path, output_path, key_path)
    - decrypt_file(input_path, output_path, key_path)
"""

from Crypto.Cipher import AES
import os


def _read_key_file(key_path: str) -> bytes:
    """Read a key file and return bytes.

    The file may contain a hex string (preferred) or UTF-8 text. The
    function validates the key length (16/24/32 bytes).

    Raises:
        FileNotFoundError: if the key file does not exist.
        ValueError: if the key has an invalid length.
    """
    if not os.path.isfile(key_path):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key_path}")

    with open(key_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    try:
        key = bytes.fromhex(content)
    except ValueError:
        key = content.encode("utf-8")
    if len(key) not in (16, 24, 32):
        raise ValueError("A chave deve ter 16, 24 ou 32 bytes (128, 192 ou 256 bits).")
    return key


def encrypt_file(input_path: str, output_path: str, key: str = ""):
    """Encrypt a file with AES-CBC and write IV||ciphertext to output.

    Args:
        input_path: Path to the plaintext input file (opened in binary).
        output_path: Path to write the encrypted file (binary).
        key: Path to the key file (hex or text).

    Raises:
        FileNotFoundError: if the key file doesn't exist.
    """
    if not os.path.isfile(key):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key}")
    key_bytes = _read_key_file(key)

    cipher = AES.new(key_bytes, AES.MODE_CBC)
    iv = cipher.iv

    with open(input_path, "rb") as f_in:
        data = f_in.read()

    pad_len = AES.block_size - (len(data) % AES.block_size)
    data += bytes([pad_len]) * pad_len

    ciphertext = cipher.encrypt(data)

    with open(output_path, "wb") as f_out:
        f_out.write(iv + ciphertext)


def decrypt_file(input_path: str, output_path: str, key: str = ""):
    """Decrypt a file produced by :func:`encrypt_file`.

    Args:
        input_path: Path to the encrypted input file.
        output_path: Path to write the decrypted plaintext.
        key: Path to the key file (hex or text).

    Raises:
        FileNotFoundError: if the key file doesn't exist.
        ValueError: if padding is invalid (likely wrong key).
    """
    if not os.path.isfile(key):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key}")
    key_bytes = _read_key_file(key)

    with open(input_path, "rb") as f_in:
        iv = f_in.read(16)
        ciphertext = f_in.read()

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv)
    data = cipher.decrypt(ciphertext)

    pad_len = data[-1]
    if pad_len < 1 or pad_len > AES.block_size:
        raise ValueError("Padding inválido ou chave incorreta.")
    data = data[:-pad_len]

    with open(output_path, "wb") as f_out:
        f_out.write(data)
