import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from src.a51 import A51Cipher
from src.tiny_a51 import TinyA51Cipher


def bit_list(text, size=None):
    text = text.strip()
    if not text or any(c not in "01" for c in text):
        raise ValueError("Chỉ nhập chuỗi 0 và 1, không để trống.")
    if size is not None and len(text) != size:
        raise ValueError(f"Phải nhập đúng {size} bit.")
    return [int(c) for c in text]


def number(text, size):
    text = text.strip()
    value = int(text, 16 if text.lower().startswith("0x") else 10)
    if not 0 <= value < (1 << size):
        raise ValueError(f"Giá trị phải là số không dấu {size} bit.")
    return value


def create_cipher(algorithm, key, frame):
    if algorithm == "TinyA5/1":
        bits = bit_list(key, 23)
        return TinyA51Cipher(bits[:6], bits[6:14], bits[14:])

    value = number(key, 64)
    bits = [
        (byte >> i) & 1
        for byte in value.to_bytes(8, "big")
        for i in range(8)
    ]
    return A51Cipher(bits, number(frame, 22))


def process_bits(cipher, bits):
    output, stream, trace = [], [], []

    for index, value in enumerate(bits, 1):
        before = [list(cipher.r1), list(cipher.r2), list(cipher.r3)]

        if isinstance(cipher, TinyA51Cipher):
            bit, log = cipher.step_verbose(index)
            clocks = log["clock_bits"]
            majority = log["majority"]
            clocked = log["clocked"]
        else:
            clocks = (cipher.r1[8], cipher.r2[10], cipher.r3[10])
            majority = int(sum(clocks) >= 2)
            clocked = tuple(c == majority for c in clocks)
            bit = cipher.get_keystream_bit()

        output.append(value ^ bit)
        stream.append(bit)
        trace.append(
            f"Bước {index}: clock={clocks}, "
            f"majority={majority}, quay={clocked}"
        )

        after = [cipher.r1, cipher.r2, cipher.r3]
        for register, (first, last) in enumerate(zip(before, after), 1):
            first_text = "".join(map(str, first))
            last_text = "".join(map(str, last))
            trace.append(f" R{register}: {first_text} -> {last_text}")

        trace.append(f" S={bit}; {value} XOR {bit} = {value ^ bit}\n")

    return (
        "".join(map(str, output)),
        "".join(map(str, stream)),
        "\n".join(trace),
    )


def process_bytes(cipher, data):
    if isinstance(cipher, A51Cipher):
        return cipher.process_bytes(data)

    output = bytearray()
    for byte in data:
        mask = 0
        for _ in range(8):
            bit, _ = cipher.step_verbose(0)
            mask = (mask << 1) | bit
        output.append(byte ^ mask)
    return bytes(output)

class App:
    def __init__(self, root):
        self.root = root
        root.title('Nhóm 9 — TinyA5/1 và A5/1')
        root.geometry('1000x820')
        self.algorithm = tk.StringVar(value='TinyA5/1')
        self.key = tk.StringVar(value='10110001010110110010101')
        self.frame = tk.StringVar(value='0x134')
        self.hint = tk.StringVar()
        self.status = tk.StringVar(value='Sẵn sàng. Chọn tab Nhị phân hoặc Văn bản / File.')
        panel = ttk.Frame(root, padding=16)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='HỆ MÃ DÒNG — NHÓM 9', font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        row = ttk.Frame(panel)
        row.pack(fill='x', pady=10)
        selector = ttk.Combobox(row, textvariable=self.algorithm, values=['TinyA5/1', 'A5/1'], state='readonly', width=13)
        selector.pack(side='left')
        selector.bind('<<ComboboxSelected>>', self.example)
        ttk.Label(row, text=' Khóa: ').pack(side='left')
        ttk.Entry(row, textvariable=self.key, width=32).pack(side='left')
        ttk.Label(row, text=' Frame: ').pack(side='left')
        self.frame_entry = ttk.Entry(row, textvariable=self.frame, width=12)
        self.frame_entry.pack(side='left')
        ttk.Button(row, text='Nạp ví dụ', command=self.example).pack(side='left', padx=8)
        ttk.Label(panel, textvariable=self.hint, wraplength=950).pack(anchor='w')
        tabs = ttk.Notebook(panel)
        tabs.pack(fill='both', expand=True, pady=10)
        self.inputs, self.outputs = {}, {}
        self.results = {'bit': '', 'text': ''}
        for mode, title in [('bit', 'Nhị phân / Tính tay'), ('text', 'Văn bản / File')]:
            tab = ttk.Frame(tabs, padding=10)
            tabs.add(tab, text=title)
            ttk.Label(tab, text='Đầu vào: chuỗi 0/1' if mode == 'bit' else 'Đầu vào: văn bản UTF-8 / bản mã hex').pack(anchor='w')
            self.inputs[mode] = ScrolledText(tab, height=4, wrap='word')
            self.inputs[mode].pack(fill='both', expand=True, pady=5)
            row = ttk.Frame(tab)
            row.pack(fill='x')
            for label, callback in [('Mã hóa', lambda m=mode: self.run(m, False)),
                                     ('Giải mã', lambda m=mode: self.run(m, True)),
                                     ('Đưa kết quả lên đầu vào', lambda m=mode: self.reuse(m))]:
                ttk.Button(row, text=label, command=callback).pack(side='left', padx=(0, 8))
            ttk.Label(tab, text='Kết quả').pack(anchor='w', pady=(8, 0))
            self.outputs[mode] = ScrolledText(tab, height=4, wrap='word', state='disabled')
            self.outputs[mode].pack(fill='both', expand=True, pady=5)
            if mode == 'bit':
                ttk.Label(tab, text='Các bước: thanh ghi trước -> sau; clock; majority; dòng khóa S').pack(anchor='w')
                self.trace = ScrolledText(tab, height=9, wrap='none', state='disabled')
                self.trace.pack(fill='both', expand=True)
            else:
                row = ttk.Frame(tab)
                row.pack(fill='x', pady=8)
                ttk.Button(row, text='Mã hóa file...', command=self.file).pack(side='left', padx=(0, 8))
                ttk.Button(row, text='Giải mã file...', command=self.file).pack(side='left')
        ttk.Label(panel, textvariable=self.status, wraplength=950).pack(anchor='w')
        ttk.Label(panel, text='Dùng đúng thuật toán, khóa và frame để giải mã. Chỉ dùng học tập; không xác thực dữ liệu.', wraplength=950).pack(anchor='w')
        self.example()

    def example(self, event=None):
        tiny = self.algorithm.get() == 'TinyA5/1'
        self.key.set('10110001010110110010101' if tiny else '0x1223456789ABCDEF')
        self.frame.set('0x134')
        self.frame_entry.configure(state='disabled' if tiny else 'normal')
        self.hint.set('Tiny 6/8/9 bit: khóa 23 bit = R1 || R2 || R3, index 0 trước; S lấy trước khi quay. Chưa xác nhận biến thể lớp.' if tiny else 'A5/1 19/22/23 bit: khóa 64 bit (số thập phân hoặc 0x...), frame 22 bit; S lấy sau khi quay.')
        for mode, value in [('bit', '1011' if tiny else '0' * 114), ('text', 'Xin chào Việt Nam!')]:
            self.inputs[mode].delete('1.0', 'end')
            self.inputs[mode].insert('1.0', value)
            self.results[mode] = ''
            self.set_output(self.outputs[mode], '')
        self.set_output(self.trace, '')

    def set_output(self, widget, value):
        widget.configure(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('1.0', value)
        widget.configure(state='disabled')

    def run(self, mode, decrypt):
        try:
            cipher = create_cipher(self.algorithm.get(), self.key.get(), self.frame.get())
            value = self.inputs[mode].get('1.0', 'end-1c')
            if mode == 'bit':
                bits = bit_list(value)
                if len(bits) > 4096:
                    raise ValueError('Tối đa 4096 bit cho bảng từng bước.')
                result, stream, trace = process_bits(cipher, bits)
                self.set_output(self.trace, trace)
                display = ('Bản rõ: ' if decrypt else 'Bản mã: ') + result + '\nDòng khóa S: ' + stream
            else:
                data = bytes.fromhex(value) if decrypt else value.encode('utf-8')
                output = process_bytes(cipher, data)
                result = output.decode('utf-8') if decrypt else output.hex()
                display = result
            self.results[mode] = result
            self.set_output(self.outputs[mode], display)
            self.status.set('Hoàn tất. Giữ nguyên khóa để giải mã.')
        except Exception as error:
            messagebox.showerror('Lỗi dữ liệu / khóa', str(error), parent=self.root)

    def reuse(self, mode):
        self.inputs[mode].delete('1.0', 'end')
        self.inputs[mode].insert('1.0', self.results[mode])

    def file(self):
        source = filedialog.askopenfilename(parent=self.root)
        if not source:
            return
        target = filedialog.asksaveasfilename(parent=self.root, title='Chọn tên file đầu ra mới')
        if not target:
            return
        try:
            if Path(target).exists():
                raise ValueError('File đầu ra đã tồn tại. Hãy chọn tên mới.')
            cipher = create_cipher(self.algorithm.get(), self.key.get(), self.frame.get())
            with open(source, 'rb') as first, open(target, 'xb') as second:
                while chunk := first.read(65536):
                    second.write(process_bytes(cipher, chunk))
            self.status.set('Đã lưu: ' + target)
        except Exception as error:
            messagebox.showerror('Lỗi file', str(error), parent=self.root)


if __name__ == "__main__":
    window = tk.Tk()
    App(window)
    window.mainloop()