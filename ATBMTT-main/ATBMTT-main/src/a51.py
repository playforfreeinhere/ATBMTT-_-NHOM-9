class A51Cipher:
    """
    Lớp cài đặt Core thuật toán A5/1 đầy đủ (Chuẩn GSM).
      - R1: 19 bits (Clock bit: R1[8], Taps: 13, 16, 17, 18)
      - R2: 22 bits (Clock bit: R2[10], Taps: 20, 21)
      - R3: 23 bits (Clock bit: R3[10], Taps: 7, 20, 21, 22)
    """

    def __init__(self, key: list[int] = None, frame_number: int = None):
        """Khởi tạo 3 thanh ghi rỗng"""
        self.r1 = [0] * 19
        self.r2 = [0] * 22
        self.r3 = [0] * 23

        if key is not None and frame_number is not None:
            self.setup_key(key, frame_number)

    def _get_majority(self, b1: int, b2: int, b3: int) -> int:
        """Hàm tính bit chiếm đa số (Majority bit)"""
        return 1 if (b1 + b2 + b3) >= 2 else 0

    def _clock_r1(self):
        """Dịch 1 nhịp thanh ghi R1 (19 bits)"""
        feedback = self.r1[18] ^ self.r1[17] ^ self.r1[16] ^ self.r1[13]
        self.r1 = [feedback] + self.r1[:-1]

    def _clock_r2(self):
        """Dịch 1 nhịp thanh ghi R2 (22 bits)"""
        feedback = self.r2[21] ^ self.r2[20]
        self.r2 = [feedback] + self.r2[:-1]

    def _clock_r3(self):
        """Dịch 1 nhịp thanh ghi R3 (23 bits)"""
        feedback = self.r3[22] ^ self.r3[21] ^ self.r3[20] ^ self.r3[7]
        self.r3 = [feedback] + self.r3[:-1]

    def clock(self, ignore_majority: bool = False):
        """
        Điều khiển dịch các thanh ghi:
          - ignore_majority=True: Dịch cả 3 thanh ghi (dùng khi nạp khóa K và Fn).
          - ignore_majority=False: Dịch theo quy tắc đa số Majority (dùng khi sinh dòng khóa).
        """
        if ignore_majority:
            self._clock_r1()
            self._clock_r2()
            self._clock_r3()
        else:
            c1, c2, c3 = self.r1[8], self.r2[10], self.r3[10]
            m = self._get_majority(c1, c2, c3)
            if c1 == m:
                self._clock_r1()
            if c2 == m:
                self._clock_r2()
            if c3 == m:
                self._clock_r3()

    def get_keystream_bit(self) -> int:
        """Sinh 1 bit dòng khóa (Keystream bit = R1[18] ^ R2[21] ^ R3[22])"""
        self.clock(ignore_majority=False)
        return self.r1[18] ^ self.r2[21] ^ self.r3[22]

    def setup_key(self, key: list[int], frame_number: int):
        """
        Quy trình nạp Khóa 64-bit K và Số khung 22-bit Frame Number (Fn) chuẩn GSM:
          1. Reset 3 thanh ghi về 0.
          2. Nạp 64 bit khóa K (dịch cả 3 thanh ghi không dùng Majority).
          3. Nạp 22 bit số khung Fn (dịch cả 3 thanh ghi không dùng Majority).
          4. Chạy 100 nhịp khởi động (warm-up cycles) theo quy tắc đa số.
        """
        self.r1 = [0] * 19
        self.r2 = [0] * 22
        self.r3 = [0] * 23

        # Nạp 64 bit khóa K
        for i in range(64):
            self.clock(ignore_majority=True)
            self.r1[0] ^= key[i]
            self.r2[0] ^= key[i]
            self.r3[0] ^= key[i]

        # Nạp 22 bit số khung Fn
        fn_bits = [(frame_number >> i) & 1 for i in range(22)]
        for i in range(22):
            self.clock(ignore_majority=True)
            self.r1[0] ^= fn_bits[i]
            self.r2[0] ^= fn_bits[i]
            self.r3[0] ^= fn_bits[i]

        # Chạy 100 nhịp xáo trộn trạng thái
        for _ in range(100):
            self.clock(ignore_majority=False)

    def process_bytes(self, data: bytes) -> bytes:
        """
        Mã hóa / Giải mã mảng bytes dữ liệu.
        Sử dụng toán tử bitwise XOR cho từng bit trong byte dữ liệu.
        Dùng chung cho cả 2 chiều Mã hóa và Giải mã.
        """
        result = bytearray()
        for byte in data:
            cipher_byte = 0
            for bit_index in range(8):
                ks_bit = self.get_keystream_bit()
                data_bit = (byte >> (7 - bit_index)) & 1
                cipher_bit = data_bit ^ ks_bit
                cipher_byte = (cipher_byte << 1) | cipher_bit
            result.append(cipher_byte)
        return bytes(result)


# --- KHỐI THỰC THI THỬ NGHIỆM ĐỘC LẬP ---
if __name__ == "__main__":
    # Khóa K (64-bit) và Số khung Fn (22-bit) mẫu
    key_64bit = [1] * 32 + [0] * 32  # 64-bit key mẫu
    fn = 0x12345                     # Frame number mẫu

    # Khởi tạo đối tượng mã hóa
    cipher_enc = A51Cipher(key_64bit, fn)
    plaintext_data = "Hệ mã dòng A5/1 - Nhóm 9".encode('utf-8')

    print("=== DEMO THUẬT TOÁN A5/1 ĐẦY ĐỦ (GSM) ===")
    print(f"Bản rõ ban đầu  : {plaintext_data.decode('utf-8')}")

    # Mã hóa
    ciphertext_data = cipher_enc.process_bytes(plaintext_data)
    print(f"Bản mã (Hex)    : {ciphertext_data.hex()}")

    # Giải mã (Cần khởi tạo lại cipher với cùng Key và Fn)
    cipher_dec = A51Cipher(key_64bit, fn)
    recovered_data = cipher_dec.process_bytes(ciphertext_data)
    print(f"Giải mã khôi phục: {recovered_data.decode('utf-8')}")

    assert recovered_data == plaintext_data, "Lỗi: Giải mã A5/1 không khớp bản rõ!"
    print("-> KIỂM THỬ THÀNH CÔNG: Mã hóa và giải mã A5/1 hoàn tất chuẩn xác.")
