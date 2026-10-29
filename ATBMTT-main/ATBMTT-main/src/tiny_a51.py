class TinyA51Cipher:
    """
    Lớp cài đặt Core thuật toán TinyA5/1 (Phiên bản thu nhỏ).
    Cấu trúc 3 thanh ghi LFSR:
      - R1: 6 bits  (Clock bit: R1[2], Taps feedback: R1[2] ^ R1[5])
      - R2: 8 bits  (Clock bit: R2[3], Taps feedback: R2[4] ^ R2[7])
      - R3: 9 bits  (Clock bit: R3[3], Taps feedback: R3[5] ^ R3[8])
    """

    def __init__(self, r1_init: list[int], r2_init: list[int], r3_init: list[int]):
        """Khởi tạo trạng thái ban đầu cho 3 thanh ghi dạng mảng bit 0/1"""
        self.r1 = list(r1_init)
        self.r2 = list(r2_init)
        self.r3 = list(r3_init)

    def _get_majority(self, c1: int, c2: int, c3: int) -> int:
        """Hàm tính bit đa số (Majority bit) tối ưu bitwise"""
        return 1 if (c1 + c2 + c3) >= 2 else 0

    def _clock_r1(self) -> int:
        """Thực hiện dịch 1 nhịp cho R1 (6 bits) bằng phép toán bitwise XOR"""
        feedback = self.r1[2] ^ self.r1[5]
        self.r1 = [feedback] + self.r1[:-1]
        return feedback

    def _clock_r2(self) -> int:
        """Thực hiện dịch 1 nhịp cho R2 (8 bits) bằng phép toán bitwise XOR"""
        feedback = self.r2[4] ^ self.r2[7]
        self.r2 = [feedback] + self.r2[:-1]
        return feedback

    def _clock_r3(self) -> int:
        """Thực hiện dịch 1 nhịp cho R3 (9 bits) bằng phép toán bitwise XOR"""
        feedback = self.r3[5] ^ self.r3[8]
        self.r3 = [feedback] + self.r3[:-1]
        return feedback

    def step_verbose(self, step_number: int) -> tuple[int, dict]:
        """
        Thực hiện 1 nhịp xử lý:
          1. Lấy bit keystream S từ trạng thái hiện tại (R1[5] ^ R2[7] ^ R3[8]).
          2. Tìm Majority bit từ 3 clock bit (R1[2], R2[3], R3[3]).
          3. Dịch nhịp các thanh ghi khớp với Majority bit.
          4. Trả về bit keystream và log trạng thái trung gian.
        """
        # 1. Trích xuất bit dòng khóa S trước khi quay nhịp mới
        keystream_bit = self.r1[5] ^ self.r2[7] ^ self.r3[8]

        # 2. Trích xuất bit kiểm soát (Clock bits)
        c1, c2, c3 = self.r1[2], self.r2[3], self.r3[3]

        # 3. Tính Majority bit
        maj = self._get_majority(c1, c2, c3)

        # 4. Xác định các thanh ghi cần quay
        clock_r1 = (c1 == maj)
        clock_r2 = (c2 == maj)
        clock_r3 = (c3 == maj)

        # 5. Dịch nhịp và ghi lại feedback
        fb1 = self._clock_r1() if clock_r1 else None
        fb2 = self._clock_r2() if clock_r2 else None
        fb3 = self._clock_r3() if clock_r3 else None

        # Đóng gói thông tin log trung gian
        log_data = {
            "step": step_number,
            "clock_bits": (c1, c2, c3),
            "majority": maj,
            "clocked": (clock_r1, clock_r2, clock_r3),
            "feedbacks": (fb1, fb2, fb3),
            "r1": list(self.r1),
            "r2": list(self.r2),
            "r3": list(self.r3),
            "keystream_bit": keystream_bit
        }

        return keystream_bit, log_data

    def generate_keystream(self, length: int) -> tuple[list[int], list[dict]]:
        """Sinh chuỗi dòng khóa gồm N bit và xuất lịch sử log"""
        keystream = []
        logs = []
        for i in range(1, length + 1):
            ks_bit, log = self.step_verbose(i)
            keystream.append(ks_bit)
            logs.append(log)
        return keystream, logs

    def process_bits(self, bit_stream: list[int]) -> tuple[list[int], list[int], list[dict]]:
        """
        Mã hóa / Giải mã chuỗi bit bản rõ bằng phép toán XOR.
        XOR có tính chất đối xứng (P ^ S = C và C ^ S = P) nên hàm xử lý được cả 2 chiều.
        """
        keystream, logs = self.generate_keystream(len(bit_stream))
        output_bits = [b ^ k for b, k in zip(bit_stream, keystream)]
        return output_bits, keystream, logs


# --- KHỐI THỰC THI THỬ NGHIỆM ĐỘC LẬP ---
if __name__ == "__main__":
    # Trạng thái ban đầu mẫu để tái hiện bài tập trên lớp
    r1_init = [1, 0, 1, 1, 0, 0]
    r2_init = [0, 1, 0, 1, 0, 1, 1, 0]
    r3_init = [1, 1, 0, 0, 1, 0, 1, 0, 1]

    cipher = TinyA51Cipher(r1_init, r2_init, r3_init)
    plaintext_bits = [1, 0, 1, 1]

    print("=== DEMO THUẬT TOÁN TINYA5/1 ===")
    cipher_bits, keystream, logs = cipher.process_bits(plaintext_bits)

    for log in logs:
        print(f"\n[Bước {log['step']}]")
        print(f"  Clock bits (C1, C2, C3) : {log['clock_bits']}")
        print(f"  Majority bit            : {log['majority']}")
        print(f"  Thanh ghi được quay     : R1={log['clocked'][0]}, R2={log['clocked'][1]}, R3={log['clocked'][2]}")
        print(f"  Bit dòng khóa (S)       : {log['keystream_bit']}")

    print("\n------------------------------------")
    print(f"Bản rõ (Plaintext) : {plaintext_bits}")
    print(f"Dòng khóa (Keystream): {keystream}")
    print(f"Bản mã (Ciphertext)  : {cipher_bits}")
    
    # Kiểm thử giải mã khôi phục bản rõ
    decipher = TinyA51Cipher(r1_init, r2_init, r3_init)
    recovered_bits, _, _ = decipher.process_bits(cipher_bits)
    print(f"Giải mã khôi phục   : {recovered_bits}")
    assert recovered_bits == plaintext_bits, "Lỗi: Giải mã không khớp bản rõ!"
    print("-> KIỂM THỬ THÀNH CÔNG: Giải mã khôi phục đúng 100% bản rõ ban đầu.")
