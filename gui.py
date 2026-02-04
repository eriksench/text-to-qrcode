#!/usr/bin/env python3
"""
GUI版本的文本转二维码工具
使用tkinter创建图形界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from PIL import Image, ImageTk
import os
from text_to_qr import TextToQRCode


class QRCodeGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文本转二维码工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 存储生成的图片对象（防止被垃圾回收）
        self.qr_images = []

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""

        # 顶部标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="文本转二维码工具",
            font=("Arial", 16, "bold")
        )
        title_label.pack()

        # 创建主容器
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # 左侧面板 - 输入区域
        left_panel = ttk.LabelFrame(main_container, text="输入文本", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 文本输入框
        self.text_input = scrolledtext.ScrolledText(
            left_panel,
            wrap=tk.WORD,
            width=40,
            height=20,
            font=("Arial", 10)
        )
        self.text_input.pack(fill=tk.BOTH, expand=True)

        # 文件操作按钮
        file_buttons_frame = ttk.Frame(left_panel)
        file_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        self.load_file_btn = ttk.Button(
            file_buttons_frame,
            text="从文件加载",
            command=self.load_from_file
        )
        self.load_file_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_btn = ttk.Button(
            file_buttons_frame,
            text="清空",
            command=self.clear_text
        )
        self.clear_btn.pack(side=tk.LEFT)

        # 右侧面板 - 设置和预览
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 设置区域
        settings_frame = ttk.LabelFrame(right_panel, text="设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # 错误纠正级别
        ttk.Label(settings_frame, text="错误纠正级别:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.error_correction_var = tk.StringVar(value="M")
        error_correction_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.error_correction_var,
            values=["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
            state="readonly",
            width=15
        )
        error_correction_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        error_correction_combo.current(1)



        # 生成按钮
        self.generate_btn = ttk.Button(
            settings_frame,
            text="生成二维码",
            command=self.generate_qrcode,
            style="Accent.TButton"
        )
        self.generate_btn.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=tk.EW)

        # 信息显示区域
        info_frame = ttk.LabelFrame(right_panel, text="文本信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.info_text = tk.Text(info_frame, height=6, width=40, font=("Courier", 9))
        self.info_text.pack(fill=tk.X)
        self.info_text.config(state=tk.DISABLED)

        # 预览区域
        preview_frame = ttk.LabelFrame(right_panel, text="二维码预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # 创建滚动容器
        preview_canvas = tk.Canvas(preview_frame)
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_canvas.yview)
        self.preview_container = ttk.Frame(preview_canvas)

        self.preview_container.bind(
            "<Configure>",
            lambda e: preview_canvas.configure(scrollregion=preview_canvas.bbox("all"))
        )

        preview_canvas.create_window((0, 0), window=self.preview_container, anchor=tk.NW)
        preview_canvas.configure(yscrollcommand=preview_scrollbar.set)

        preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 底部状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(
            status_frame,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_label.pack(fill=tk.X)

    def load_from_file(self):
        """从文件加载文本"""
        filename = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_input.delete(1.0, tk.END)
                    self.text_input.insert(1.0, content)
                    self.status_label.config(text=f"已加载文件: {os.path.basename(filename)}")
                    self.update_info()
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败:\n{str(e)}")

    def clear_text(self):
        """清空文本"""
        self.text_input.delete(1.0, tk.END)
        self.update_info()
        self.status_label.config(text="已清空文本")

    def get_error_correction_level(self):
        """获取错误纠正级别"""
        value = self.error_correction_var.get()
        return value[0]  # 返回 'L', 'M', 'Q', 或 'H'

    def update_info(self):
        """更新文本信息显示"""
        text = self.text_input.get(1.0, tk.END).strip()

        if not text:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, "暂无文本")
            self.info_text.config(state=tk.DISABLED)
            return

        converter = TextToQRCode(error_correction=self.get_error_correction_level())
        info = converter.get_text_info(text)

        info_str = f"""字符数: {info['char_count']}
字节数: {info['byte_count']}
纠错级别: {info['error_correction']}
单个容量: {info['max_bytes_per_qr']} 字节
二维码数: {info['num_qrcodes']}"""

        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_str)
        self.info_text.config(state=tk.DISABLED)

    def generate_qrcode(self):
        """生成二维码"""
        text = self.text_input.get(1.0, tk.END).strip()

        if not text:
            messagebox.showwarning("警告", "请先输入要转换的文本")
            return

        # 清空之前的预览
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        self.qr_images.clear()

        # 更新状态
        self.status_label.config(text="正在生成二维码...")
        self.root.update()

        try:
            # 创建转换器
            converter = TextToQRCode(
                error_correction=self.get_error_correction_level(),
                box_size=10,
                border=4
            )

            # 生成二维码（不保存文件）
            qr_images_data = converter.generate_qrcode_images(text)

            # 显示预览
            for i, (img, text_part) in enumerate(qr_images_data):
                # 创建每个二维码的框架
                qr_frame = ttk.Frame(self.preview_container, padding="5")
                qr_frame.pack(fill=tk.X, pady=5)

                # 标题
                if len(qr_images_data) > 1:
                    title = f"二维码 {i+1}/{len(qr_images_data)}"
                else:
                    title = "二维码"

                title_label = ttk.Label(qr_frame, text=title, font=("Arial", 10, "bold"))
                title_label.pack()

                # 调整大小以适应预览
                img_copy = img.copy()
                img_copy.thumbnail((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_copy)
                self.qr_images.append(photo)  # 保持引用

                img_label = ttk.Label(qr_frame, image=photo)
                img_label.pack(pady=5)

            # 更新状态
            if len(qr_images_data) > 1:
                self.status_label.config(
                    text=f"成功生成 {len(qr_images_data)} 个二维码！请按顺序扫描。"
                )
            else:
                self.status_label.config(text="成功生成二维码！")

        except Exception as e:
            messagebox.showerror("错误", f"生成二维码失败:\n{str(e)}")
            self.status_label.config(text="生成失败")


def main():
    root = tk.Tk()

    # 设置应用图标（如果需要）
    try:
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass

    app = QRCodeGeneratorGUI(root)

    # 绑定文本变化事件
    def on_text_change(event=None):
        app.update_info()

    app.text_input.bind('<<Modified>>', lambda e: (
        app.text_input.edit_modified(False),
        on_text_change()
    ))

    root.mainloop()


if __name__ == "__main__":
    main()
