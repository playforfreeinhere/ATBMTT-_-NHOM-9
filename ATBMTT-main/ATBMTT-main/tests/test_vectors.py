import pytest

from src.tiny_a51 import TinyA51


def test_keystream_repeatability():
    key = 0x1A2B3C
    t1 = TinyA51(key)
    t2 = TinyA51(key)
    a = t1.keystream_bytes(16)
    b = t2.keystream_bytes(16)
    assert a == b


def test_encrypt_decrypt_roundtrip():
    key = 0xDEADBEEF
    t = TinyA51(key)
    data = b"Test data for encryption".ljust(32, b"\x00")
    c = t.encrypt(data)
    # reset generator
    t2 = TinyA51(key)
    p = t2.decrypt(c)
    assert p == data
