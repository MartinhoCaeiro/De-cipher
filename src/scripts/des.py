"""DES file encrypt/decrypt helpers (ECB mode).

Small helpers to encrypt and decrypt files using DES-ECB. The key is
read from a file that may contain a hex string or raw UTF-8 text. The
encrypted output format is the raw ciphertext (no IV).
"""

from Crypto.Cipher import DES
import os


def _read_key_file(key_path: str) -> bytes:
    """Read a DES key from a file and return it as bytes.

    The file may contain a hex-encoded key or plain UTF-8 text. The
    returned key must be exactly 8 bytes long.

    Raises:
        FileNotFoundError: if the key file does not exist.
        ValueError: if the key length is not 8 bytes.
    """
    if not os.path.isfile(key_path):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key_path}")

    with open(key_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    try:
        key = bytes.fromhex(content)
    except ValueError:
        key = content.encode()

    if len(key) != 8:
        raise ValueError("A chave DES deve ter exatamente 8 bytes (64 bits).")
    return key


def encrypt_file(input_path: str, output_path: str, key_path: str):
    """Encrypt a file using DES-CBC and write IV||ciphertext to output.
    Encrypt a file using DES-ECB and write the raw ciphertext to output.

    Args:
        input_path: Path to the plaintext file (binary).
        output_path: Path where the encrypted file will be written.
        key_path: Path to the key file (hex or text).
    """
    key = _read_key_file(key_path)
    cipher = DES.new(key, DES.MODE_ECB)

    with open(input_path, "rb") as f:
        data = f.read()

    pad = DES.block_size - (len(data) % DES.block_size)
    ciphertext = cipher.encrypt(data + bytes([pad]) * pad)

    with open(output_path, "wb") as f:
        f.write(ciphertext)


def decrypt_file(input_path: str, output_path: str, key_path: str):
    """Decrypt a file produced by :func:`encrypt_file` and write plaintext.

    Args:
        input_path: Path to the encrypted input file.
        output_path: Path to write the recovered plaintext.
        key_path: Path to the key file (hex or text).

    Raises:
        ValueError: if padding is invalid (likely wrong key).
    """
    key = _read_key_file(key_path)
    cipher = DES.new(key, DES.MODE_ECB)

    with open(input_path, "rb") as f:
        data = cipher.decrypt(f.read())

    pad = data[-1]
    if not 1 <= pad <= DES.block_size:
        raise ValueError("Padding inválido ou chave incorreta.")

    with open(output_path, "wb") as f:
        f.write(data[:-pad])
