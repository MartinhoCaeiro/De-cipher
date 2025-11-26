# (De)cipher™

(De)cipher™ is an educational file encryption/decryption application written in Python. It was developed for the course "Cryptography and Applied Cryptanalysis" and implements four symmetric ciphers:

- AES (ECB mode, PKCS#7 padding)
- DES (ECB mode, PKCS#5 padding)
- Vigenère (custom 95x95 table)
- Playfair (custom 5×5 board)

This repository includes the code, resources (keys, tables, GUI screenshot) and a detailed project report in Portuguese (Relatorio.tex) describing the design decisions, formats and tests.

## Quick summary

- GUI-driven application for encrypting and decrypting files.
- AES/DES produce binary files where the IV is prefixed to the ciphertext (IV || ciphertext).
- Vigenère/Playfair operate on normalized text (A–Z uppercase) and write outputs as letters only.
- The application validates keys/tables and raises clear errors for missing/invalid inputs or invalid padding.

## Requirements

- Python 3.8+
- pycryptodome
- tkinter (usually included with Python on most platforms)
- Any other GUI dependencies used by the project 


## Repository layout (indicative)
- gui.py                 — main GUI script
- aes.py                 — AES implementation (ECB)
- des.py                 — DES implementation (ECB)
- vigenere.py            — Vigenère implementation
- playfair.py            — Playfair implementation
- Recursos/              — resources used by the report and GUI (images, tables, keys)
  - Logos/
  - GUI.png
  - referencias.bib
- Relatorio.tex          — LaTeX report describing implementation and tests

Note: File names and layout are described based on the report.

## Usage (GUI)

Start the GUI:
```bash
python gui.py
```

Typical GUI flow:
1. Open the GUI.
2. Choose a tab for AES, DES, Vigenère or Playfair.
3. Select input file and output file locations.
4. Select key file (or table/board file) when required.
5. Click "Encrypt" or "Decrypt".
6. Read success or error messages from the GUI.

## Usage (command-line examples)

The repository is primarily GUI-driven, but the modules support command-line style examples (actual script arguments may differ; check each script for exact CLI options). Example hypothetical calls:

AES:
```bash
python aes.py encrypt --key-file keys/aes.key --in plain.txt --out encrypted.aes
python aes.py decrypt --key-file keys/aes.key --in encrypted.aes --out decrypted.txt
```

DES:
```bash
python des.py encrypt --key-file keys/des.key --in plain.txt --out encrypted.des
python des.py decrypt --key-file keys/des.key --in encrypted.des --out decrypted.txt
```

Vigenère:
```bash
python vigenere.py encrypt --table Recursos/vigenere_table.txt --key keys/vig.key --in plain.txt --out encrypted.vig
python vigenere.py decrypt --table Recursos/vigenere_table.txt --key keys/vig.key --in encrypted.vig --out decrypted.txt
```

Playfair:
```bash
python playfair.py encrypt --board Recursos/playfair_board.txt --in plain.txt --out encrypted.pf
python playfair.py decrypt --board Recursos/playfair_board.txt --in encrypted.pf --out decrypted.txt
```

Check the scripts for exact argument names and behavior — the above are example command patterns matching the behavior described in the report.

## Formats and implementation notes

- AES
  - Format: IV (16 bytes) || ciphertext
  - Key lengths accepted: 16, 24, or 32 bytes (hex preferred, fallback UTF-8)
  - Padding: PKCS#7
  - Library: PyCryptodome

- DES
  - Format: IV (8 bytes) || ciphertext
  - Key length accepted: exactly 8 bytes (hex preferred, fallback UTF-8)
  - Padding: PKCS#5 (8-byte block)
  - Library: PyCryptodome

- Vigenère
  - Requires a 95x95 table file (lines with 96 ASCII characters)
  - Key file: letters A–Z only, returned as uppercase
  - Input is normalized to uppercase A–Z; non-letter characters are removed
  - Output contains only uppercase letters A–Z

- Playfair
  - Requires a 5×5 board file; non-alphabetic characters ignored and 'J' mapped to 'I'
  - Message normalization: uppercase letters, insert 'X' between duplicate letters in a digraph, append 'X' if final length is odd
  - Output contains uppercase letters A–Z with 'J' mapped to 'I'

Errors and exceptions:
- Missing or malformed key/table files raise descriptive exceptions.
- Invalid key length, invalid table format, nonexistent files and invalid padding all produce explicit errors shown in the GUI or raised by the CLI scripts.

## Tests and examples

The report (Relatorio.tex) contains screenshots and a description of the tests used to validate each cipher implementation. Example keys and tables used for testing are expected to be in Recursos/ (verify presence). To reproduce tests, use those resources via the GUI or the scripts.

## Contributing

Contributions are welcome:
- Open an issue describing the bug or feature.
- Create a feature branch for your changes.
- Submit a pull request with a clear description and tests where appropriate.
