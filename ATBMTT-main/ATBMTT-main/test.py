import os
import time

# ==============================================================================
# MODULE 1: THUẬT TOÁN A5/1 LÕI (PURE IMPLEMENTATION)
# ==============================================================================

class TinyA51:
    """Phiên bản TinyA5/1 phục vụ giảng dạy và đối chiếu tính tay"""
    def __init__(self, r1_init: int, r2_init: int, r3_init: int):
        self.r1 = r1_init & 0x3F  # 6 bit (0..63)
        self.r2 = r2_init & 0x7F  # 7 bit (0..127)
        self.r3 = r3_init & 0xFF  # 8 bit (0..255)

    def _get_bit(self, val: int, pos: int, length: int) -> int:
        """Lấy bit tại vị trí pos (0-indexed từ trái sang phải)"""
        shift = length - 1 - pos
        return (val >> shift) & 1

    def step(self) -> int:
        # Bit clock: R1[1], R2[3], R3[3]
        c1 = self._get_bit(self.r1, 1, 6)
        c2 = self._get_bit(self.r2, 3, 7)
        c3 = self._get_bit(self.r3, 3, 8)

        # Tính majority
        maj = (c1 & c2) | (c2 & c3) | (c3 & c1)

        # Tính bit phản hồi (Feedback bits)
        # R1: tap 5, 2
        fb1 = self._get_bit(self.r1, 5, 6) ^ self._get_bit(self.r1, 2, 6)
        # R2: tap 6, 1
        fb2 = self._get_bit(self.r2, 6, 7) ^ self._get_bit(self.r2, 1, 7)
        # R3: tap 7, 3, 1, 0
        fb3 = (self._get_bit(self.r3, 7, 8) ^ self._get_bit(self.r3, 3, 8) ^ 
               self._get_bit(self.r3, 1, 8) ^ self._get_bit(self.r3, 0, 8))

        # Dịch thanh ghi nếu bit clock == maj
        if c1 == maj:
            self.r1 = ((self.r1 << 1) & 0x3F) | fb1
        if c2 == maj:
            self.r2 = ((self.r2 << 1) & 0x7F) | fb2
        if c3 == maj:
            self.r3 = ((self.r3 << 1) & 0xFF) | fb3

        # Bit ra keystream là XOR các MSB (bit 5 của R1, bit 6 của R2, bit 7 của R3)
        out_bit = self._get_bit(self.r1, 5, 6) ^ self._get_bit(self.r2, 6, 7) ^ self._get_bit(self.r3, 7, 8)
        return out_bit


class FullA51:
    """Phiên bản A5/1 chuẩn GSM (19 + 22 + 23 bits)"""
    def __init__(self, key_64bit: int, frame_22bit: int):
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self._key_setup(key_64bit, frame_22bit)

    def _clock_all(self, fb1=0, fb2=0, fb3=0):
        # Nạp bit mới vào LSB
        r1_fb = ((self.r1 >> 18) ^ (self.r1 >> 17) ^ (self.r1 >> 16) ^ (self.r1 >> 13)) & 1
        r2_fb = ((self.r2 >> 21) ^ (self.r2 >> 20)) & 1
        r3_fb = ((self.r3 >> 22) ^ (self.r3 >> 21) ^ (self.r3 >> 17) ^ (self.r3 >> 16)) & 1

        self.r1 = ((self.r1 << 1) & 0x7FFFF) | (r1_fb ^ fb1)
        self.r2 = ((self.r2 << 1) & 0x3FFFFF) | (r2_fb ^ fb2)
        self.r3 = ((self.r3 << 1) & 0x7FFFFF) | (r3_fb ^ fb3)

    def _key_setup(self, key: int, frame: int):
        # 1. Nạp Key 64-bit
        for i in range(64):
            k_i = (key >> i) & 1
            self._clock_all(k_i, k_i, k_i)

        # 2. Nạp Frame Number 22-bit
        for i in range(22):
            f_i = (frame >> i) & 1
            self._clock_all(f_i, f_i, f_i)

        # 3. Quay 100 chu kỳ theo luật Majority không sinh bit
        for _ in range(100):
            self.step_with_majority(produce_bit=False)

    def step_with_majority(self, produce_bit=True) -> int:
        c1 = (self.r1 >> 8) & 1
        c2 = (self.r2 >> 10) & 1
        c3 = (self.r3 >> 10) & 1

        maj = (c1 & c2) | (c2 & c3) | (c3 & c1)

        r1_fb = ((self.r1 >> 18) ^ (self.r1 >> 17) ^ (self.r1 >> 16) ^ (self.r1 >> 13)) & 1
        r2_fb = ((self.r2 >> 21) ^ (self.r2 >> 20)) & 1
        r3_fb = ((self.r3 >> 22) ^ (self.r3 >> 21) ^ (self.r3 >> 17) ^ (self.r3 >> 16)) & 1

        if c1 == maj:
            self.r1 = ((self.r1 << 1) & 0x7FFFF) | r1_fb
        if c2 == maj:
            self.r2 = ((self.r2 << 1) & 0x3FFFFF) | r2_fb
        if c3 == maj:
            self.r3 = ((self.r3 << 1) & 0x7FFFFF) | r3_fb

        if produce_bit:
            return ((self.r1 >> 18) ^ (self.r2 >> 21) ^ (self.r3 >> 22)) & 1
        return 0

    def generate_byte(self) -> int:
        byte_val = 0
        for _ in range(8):
            bit = self.step_with_majority(produce_bit=True)
            byte_val = (byte_val << 1) | bit
        return byte_val


# ==============================================================================
# MODULE 2: GIAO DIỆN XỬ LÝ DỮ LIỆU & FILE (CIPHER SERVICE)
# ==============================================================================

def encrypt_decrypt_bytes(data: bytes, key_64bit: int, frame_22bit: int) -> bytes:
    cipher = FullA51(key_64bit, frame_22bit)
    out = bytearray()
    for b in data:
        keystream_byte = cipher.generate_byte()
        out.append(b ^ keystream_byte)
    return bytes(out)


def encrypt_file(input_path: str, output_path: str, key: int, frame: int):
    with open(input_path, 'rb') as f:
        data = f.read()
    
    t0 = time.time()
    res = encrypt_decrypt_bytes(data, key, frame)
    t1 = time.time()
    
    with open(output_path, 'wb') as f:
        f.write(res)
    print(f"[+] Đã xử lý tệp '{input_path}' -> '{output_path}' trong {t1-t0:.4f}s ({len(data)} bytes).")


# ==============================================================================
# MODULE 3: KIỂM THỬ VÀ DEMO CHƯƠNG TRÌNH (TEST & CLI)
# ==============================================================================

def run_tests():
    print("=== TEST 1: TINYA5/1 TÍNH TAY DỰA TRÊN VÍ DỤ BÁO CÁO ===")
    # Khởi tạo R1 = 0b101100 (44), R2 = 0b0101101 (45), R3 = 0b11010010 (210)
    tiny = TinyA51(r1_init=0b101100, r2_init=0b0101101, r3_init=0b11010010)
    s1 = tiny.step()
    s2 = tiny.step()
    print(f"Bit keystream 1: {s1} (Kỳ vọng: 1)")
    print(f"Bit keystream 2: {s2} (Kỳ vọng: 1)")
    assert s1 == 1 and s2 == 1, "❌ Lỗi: Kết quả TinyA5/1 không khớp tính tay!"
    print("=> PASS Test TinyA5/1!\n")

    print("=== TEST 2: KIỂM TRA ĐÍNH CHÍNH MÃ HÓA / GIẢI MÃ (FULL A5/1) ===")
    plaintext = b"A5/1 Stream Cipher Implementation - FIT NEU 2026"
    key = 0x123456789ABCDEF0
    frame = 0x123456

    ciphertext = encrypt_decrypt_bytes(plaintext, key, frame)
    decrypted = encrypt_decrypt_bytes(ciphertext, key, frame)

    print(f"Bản rõ ban đầu : {plaintext}")
    print(f"Bản mã (Hex)   : {ciphertext.hex()}")
    print(f"Bản giải mã    : {decrypted}")
    assert plaintext == decrypted, "❌ Lỗi: Giải mã không đúng bản rõ!"
    print("=> PASS Test Mã hóa / Giải mã thành công!\n")


def main():
    run_tests()

    print("=== DEMO XỬ LÝ FILE ẢNH/VĂN BẢN THẬT ===")
    dummy_filename = "demo_test.txt"
    enc_filename = "demo_test.enc"
    dec_filename = "demo_test_dec.txt"

    # Tạo tệp dữ liệu giả lập
    with open(dummy_filename, "w", encoding="utf-8") as f:
        f.write("Xin chào, đây là bài tập lớn An toàn thông tin hệ mã A5/1!\n" * 100)

    key = 0xFEDCBA9876543210
    frame = 0x3FFFFF

    # Mã hóa
    encrypt_file(dummy_filename, enc_filename, key, frame)
    # Giải mã
    encrypt_file(enc_filename, dec_filename, key, frame)

    # Đọc đối chiếu
    with open(dummy_filename, "rb") as f1, open(dec_filename, "rb") as f2:
        if f1.read() == f2.read():
            print("\n[SUCCESS] Khôi phục chính xác 100% dữ liệu gốc!")
        else:
            print("\n[ERROR] Dữ liệu giải mã bị sai lệch!")

    # Dọn dẹp
    for fn in [dummy_filename, enc_filename, dec_filename]:
        if os.path.exists(fn):
            os.remove(fn)


if __name__ == "__main__":
    main()