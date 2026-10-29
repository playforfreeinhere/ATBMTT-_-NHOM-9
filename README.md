# ATBMTT — Hệ mã dòng A5/1 & TinyA5/1

Dự án: Hệ mã dòng A5/1 và TinyA5/1

Nhóm: Nhóm 9
Thành viên:
- Thành viên 1: Trịnh Duy Thành 
- Thành viên 2: Nguyên Như Chí Kiên
- Thành viên 3: Lê Tuấn Hưng
- Thành viên 4: Nguyễn Thanh Thảo

Mô tả
------
Bộ mã nguồn này chứa triển khai tham chiếu của thuật toán A5/1 và một phiên bản rút gọn TinyA5/1, kèm theo giao diện đơn giản, bộ kiểm thử và mã minh họa cho các trường hợp tấn công khác nhau.

Mục tiêu
-------
- Thực hiện và so sánh TinyA5/1 với A5/1 đầy đủ.
- Viết unit tests để kiểm chứng kết quả với vectơ kiểm thử.
- Minh họa tấn công khi tái sử dụng dòng khóa (keystream reuse).

Yêu cầu môi trường
------------------
- Python 3.10+

Cài đặt phụ thuộc
------------------
Tệp requirements.txt chứa các phụ thuộc tối thiểu. Cài đặt bằng:

```bash
python -m pip install -r requirements.txt
```

Cấu trúc dự án
---------------
- src/ — Mã nguồn lõi (tiny_a51.py, a51.py)
- ui/ — Giao diện CLI thử nghiệm (module ui.cli)
- tests/ — Unit tests (pytest)
- attacks/ — Ví dụ tấn công (keystream reuse)
- data/ — Tệp minh họa input/output
- README.md — Tài liệu hướng dẫn
- requirements.txt — Thư viện cần thiết

Hướng dẫn chạy
---------------
1. Cài đặt phụ thuộc:

```bash
python -m pip install -r requirements.txt
```

2. Chạy CLI mã hóa/giải mã mẫu:

```bash
python -m ui.cli encrypt data/sample_plain.txt data/sample_encrypted.bin 0x1A2B3C4D
python -m ui.cli decrypt data/sample_encrypted.bin data/sample_decrypted.txt 0x1A2B3C4D
```

3. Chạy unit tests:

```bash
pytest -q
```

Ghi chú về đóng góp
-------------------
Để lịch sử commit thể hiện đóng góp của từng thành viên, mỗi thành viên nên:

```bash
git clone https://github.com/playforfreeinhere/ATBMTT.git
git checkout -b feature/<ten-thanh-vien>
# thực hiện thay đổi, commit rồi push
git push origin feature/<ten-thanh-vien>
```

Tài liệu nộp bài (bên ngoài GitHub)
----------------------------------
- Báo cáo Word: Phân tích, sơ đồ khối, tính tay ví dụ TinyA5/1 đối chiếu với kết quả chương trình, phân công công việc.
- Slide thuyết trình.
- Video demo (3–5 phút): Quay màn hình minh họa chạy chương trình, unit test, và log nội bộ TinyA5/1.

Tiếp theo
--------
Tôi đã thêm các tệp mã nguồn mẫu, test, demo tấn công và dữ liệu mẫu. Nếu bạn muốn, tôi sẽ mở rộng phần triển khai thuật toán TinyA5/1 và A5/1 hoặc di chuyển dự án sang cấu trúc package rõ ràng hơn.
