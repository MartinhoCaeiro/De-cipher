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
    """
    if not os.path.isfile(key_path):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key_path}")

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
    """Encrypt a file using DES-CBC and write IV||ciphertext to output.
    Encrypt a file using DES-ECB and write the raw ciphertext to output.

    Args:
        input_path: Path to the plaintext file (binary).
        output_path: Path where the encrypted file will be written.
        key: Path to the key file (hex or text).
    """
    if not os.path.isfile(key):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key}")
    key_bytes = _read_key_file(key)

    cipher = DES.new(key_bytes, DES.MODE_ECB)

    with open(input_path, "rb") as f_in:
        data = f_in.read()

    pad_len = DES.block_size - (len(data) % DES.block_size)
    data += bytes([pad_len]) * pad_len

    ciphertext = cipher.encrypt(data)

    with open(output_path, "wb") as f_out:
        f_out.write(ciphertext)


def decrypt_file(input_path: str, output_path: str, key: str = ""):
    """Decrypt a file produced by :func:`encrypt_file` and write plaintext.

    Args:
        input_path: Path to the encrypted input file.
        output_path: Path to write the recovered plaintext.
        key: Path to the key file (hex or text).
    """
    if not os.path.isfile(key):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key}")
    key_bytes = _read_key_file(key)
    with open(input_path, "rb") as f_in:
        ciphertext = f_in.read()

    cipher = DES.new(key_bytes, DES.MODE_ECB)
    data = cipher.decrypt(ciphertext)

    pad_len = data[-1]
    if pad_len < 1 or pad_len > DES.block_size:
        raise ValueError("Padding inválido ou chave incorreta.")
    data = data[:-pad_len]

    with open(output_path, "wb") as f_out:
        f_out.write(data)
