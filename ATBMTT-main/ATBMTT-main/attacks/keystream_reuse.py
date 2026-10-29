"""
Demonstration script showing keystream reuse attack: encrypt two plaintexts with same key and show that XOR of ciphertexts = XOR of plaintexts.
"""
from src.tiny_a51 import TinyA51


def demo_reuse(plain1: bytes, plain2: bytes, key: int):
    t1 = TinyA51(key)
    c1 = t1.encrypt(plain1)
    t2 = TinyA51(key)
    c2 = t2.encrypt(plain2)
    # if keystream reused, c1 ^ c2 = p1 ^ p2
    import itertools
    xored = bytes(a ^ b for a, b in zip(c1, c2))
    return c1, c2, xored


if __name__ == "__main__":
    p1 = b"Hello, this is message A.".ljust(64, b" ")
    p2 = b"Attack at dawn! This is message B.".ljust(64, b" ")
    c1, c2, x = demo_reuse(p1, p2, key=0x12345)
    print("Cipher1:", c1.hex())
    print("Cipher2:", c2.hex())
    print("XOR (should equal p1^p2):", x.hex())
    print("p1^p2:", bytes(a ^ b for a, b in zip(p1, p2)).hex())
