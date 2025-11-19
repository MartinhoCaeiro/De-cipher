"""AES file encrypt/decrypt helpers (ECB mode).

This module provides a minimal helper API to encrypt and decrypt files
using AES in ECB mode. The key is loaded from a file which may contain
either a hex string or raw UTF-8 text. The encrypted output format is
the raw ciphertext (no IV).

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
        key = content.encode()

    if len(key) not in (16, 24, 32):
        raise ValueError("A chave deve ter 16, 24 ou 32 bytes.")
    return key


def encrypt_file(input_path: str, output_path: str, key_path: str):
    """Encrypt a file with AES-ECB and write ciphertext to output.

    Args:
        input_path: Path to the plaintext input file (opened in binary).
        output_path: Path to write the encrypted file (binary).
        key_path: Path to the key file (hex or text).

    """
    key = _read_key_file(key_path)
    cipher = AES.new(key, AES.MODE_ECB)

    with open(input_path, "rb") as f:
        data = f.read()

    pad = AES.block_size - len(data) % AES.block_size
    ciphertext = cipher.encrypt(data + bytes([pad])*pad)

    with open(output_path, "wb") as f:
        f.write(ciphertext)


def decrypt_file(input_path: str, output_path: str, key_path: str):
    """Decrypt a file produced by :func:`encrypt_file` (ECB mode).

    Args:
        input_path: Path to the encrypted input file.
        output_path: Path to write the decrypted plaintext.
        key_path: Path to the key file (hex or text).

    Raises:
        ValueError: if padding is invalid (likely wrong key).
    """
    key = _read_key_file(key_path)
    cipher = AES.new(key, AES.MODE_ECB)

    with open(input_path, "rb") as f:
        data = cipher.decrypt(f.read())

    pad = data[-1]
    if not 1 <= pad <= AES.block_size:
        raise ValueError("Padding inválido ou chave incorreta.")

    with open(output_path, "wb") as f:
        f.write(data[:-pad])