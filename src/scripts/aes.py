# scripts/aes.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

def _read_key_file(key_path: str) -> bytes:
    """Lê a chave de um ficheiro de texto (como string hexadecimal ou bytes)."""
    with open(key_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    try:
        # Tenta interpretar como hex
        key = bytes.fromhex(content)
    except ValueError:
        # Caso contrário, usa texto direto (UTF-8)
        key = content.encode("utf-8")
    if len(key) not in (16, 24, 32):
        raise ValueError("A chave deve ter 128, 192 ou 256 bits (16, 24 ou 32 bytes).")
    return key


def encrypt_file(input_path: str, output_path: str, key: str = ""):
    """Cifra um ficheiro com AES (modo CBC)."""
    if not os.path.isfile(key):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key}")
    key_bytes = _read_key_file(key)

    cipher = AES.new(key_bytes, AES.MODE_CBC)
    iv = cipher.iv

    with open(input_path, "rb") as f_in:
        data = f_in.read()

    # Padding (PKCS7)
    pad_len = AES.block_size - (len(data) % AES.block_size)
    data += bytes([pad_len]) * pad_len

    ciphertext = cipher.encrypt(data)

    with open(output_path, "wb") as f_out:
        # Guarda IV + dados cifrados
        f_out.write(iv + ciphertext)


def decrypt_file(input_path: str, output_path: str, key: str = ""):
    """Decifra um ficheiro cifrado com AES (modo CBC)."""
    if not os.path.isfile(key):
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key}")
    key_bytes = _read_key_file(key)

    with open(input_path, "rb") as f_in:
        iv = f_in.read(16)
        ciphertext = f_in.read()

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv)
    data = cipher.decrypt(ciphertext)

    # Remove padding
    pad_len = data[-1]
    if pad_len < 1 or pad_len > AES.block_size:
        raise ValueError("Padding inválido ou chave incorreta.")
    data = data[:-pad_len]

    with open(output_path, "wb") as f_out:
        f_out.write(data)
