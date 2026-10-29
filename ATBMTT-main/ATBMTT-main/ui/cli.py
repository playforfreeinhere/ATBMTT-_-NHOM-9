"""
Simple CLI wrapper to encrypt/decrypt files using the tiny A5/1 implementation.
Usage:
    python -m ui.cli encrypt input.txt output.bin <key>
    python -m ui.cli decrypt input.bin output.txt <key>

Key can be given as integer or hex (prefix 0x).
"""
import sys
import os
from pathlib import Path

from src.tiny_a51 import TinyA51


def parse_key(s: str) -> int:
    s = s.strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(s)


def encrypt_file(in_path: str, out_path: str, key: int):
    p = Path(in_path)
    data = p.read_bytes()
    t = TinyA51(key)
    out = t.encrypt(data)
    Path(out_path).write_bytes(out)
    print(f"Encrypted {in_path} -> {out_path} ({len(data)} bytes)")


def decrypt_file(in_path: str, out_path: str, key: int):
    encrypt_file(in_path, out_path, key)  # symmetric for stream cipher


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        return
    cmd = sys.argv[1].lower()
    if cmd not in ("encrypt", "decrypt"):
        print("First argument must be 'encrypt' or 'decrypt'")
        return
    in_path = sys.argv[2]
    out_path = sys.argv[3]
    key = parse_key(sys.argv[4])
    if cmd == "encrypt":
        encrypt_file(in_path, out_path, key)
    else:
        decrypt_file(in_path, out_path, key)


if __name__ == "__main__":
    main()
