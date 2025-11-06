import os
import sys
# Ensure the scripts directory is on sys.path so we can import playfair
sys.path.insert(0, os.path.dirname(__file__))

from playfair import fix_message

cases = [
    "Hello, World! 123",
    "!@#$%^&*()_+|~-=`{}[]:\\;\"'<>,.?/",
    "MixEd CaSe and J vs I",
    "Repeatedttt letters!!!",
]

print("Testing fix_message acceptance of ASCII 33..125:\n")
for c in cases:
    out = fix_message(c)
    print(f"IN : {c}")
    print(f"OUT: {out}\n")
