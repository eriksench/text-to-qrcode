"""
文本转二维码核心模块
用于将文本内容转换为二维码图片
"""

import qrcode
from PIL import Image
import math


class TextToQRCode:
    """文本转二维码转换器"""

    # 二维码容量限制（字节）
    # Low error correction: ~2953 bytes
    # Medium: ~2331 bytes
    # Quartile: ~1663 bytes
    # High: ~1273 bytes
    MAX_BYTES_PER_QR = {
        'L': 2900,  # Low - 7% error correction
        'M': 2300,  # Medium - 15% error correction
        'Q': 1600,  # Quartile - 25% error correction
        'H': 1200   # High - 30% error correction
    }

    def __init__(self, error_correction='M', box_size=10, border=4):
        """
        初始化二维码生成器

        Args:
            error_correction: 错误纠正级别 ('L', 'M', 'Q', 'H')
            box_size: 每个小方块的像素大小
            border: 边框大小（小方块数量）
        """
        self.error_correction_level = error_correction
        self.box_size = box_size
        self.border = border

        # 设置错误纠正级别
        self.error_correction_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }

    def split_text(self, text):
        """
        将长文本分割成多个片段

        Args:
            text: 原始文本

        Returns:
            list: 文本片段列表
        """
        max_bytes = self.MAX_BYTES_PER_QR[self.error_correction_level]
        text_bytes = text.encode('utf-8')

        if len(text_bytes) <= max_bytes:
            return [text]

        # 计算需要分成多少个二维码
        num_parts = math.ceil(len(text_bytes) / max_bytes)
        parts = []

        # 分割文本，确保不会在UTF-8字符中间切断
        start = 0
        for i in range(num_parts):
            # 计算这一段的结束位置
            end = min(start + max_bytes, len(text_bytes))

            # 确保不会在UTF-8字符中间切断
            while end < len(text_bytes):
                try:
                    # 尝试解码，如果成功则说明没有切断字符
                    text_bytes[start:end].decode('utf-8')
                    break
                except UnicodeDecodeError:
                    # 如果失败，向前移动一个字节
                    end -= 1

            part_text = text_bytes[start:end].decode('utf-8')
            # 添加分页信息
            if num_parts > 1:
                parts.append(f"[{i+1}/{num_parts}]\n{part_text}")
            else:
                parts.append(part_text)

            start = end

        return parts

    def generate_qrcode(self, text):
        """
        生成单个二维码

        Args:
            text: 要转换的文本

        Returns:
            PIL.Image: 二维码图片对象
        """
        qr = qrcode.QRCode(
            version=None,  # 自动选择版本
            error_correction=self.error_correction_map[self.error_correction_level],
            box_size=self.box_size,
            border=self.border,
        )

        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img

    def generate_qrcode_images(self, text):
        """
        生成二维码图片对象（不保存到文件）

        Args:
            text: 要转换的文本

        Returns:
            list: 包含 (PIL.Image, 文本片段) 元组的列表
        """
        # 分割文本
        text_parts = self.split_text(text)

        # 生成二维码
        images = []
        for part in text_parts:
            img = self.generate_qrcode(part)
            images.append((img, part))

        return images

    def text_to_qrcode(self, text, output_prefix="qrcode"):
        """
        将文本转换为二维码图片

        Args:
            text: 要转换的文本
            output_prefix: 输出文件名前缀

        Returns:
            list: 生成的图片文件路径列表
        """
        # 分割文本
        text_parts = self.split_text(text)

        # 生成二维码
        image_paths = []
        for i, part in enumerate(text_parts):
            img = self.generate_qrcode(part)

            if len(text_parts) > 1:
                filename = f"{output_prefix}_{i+1}_of_{len(text_parts)}.png"
            else:
                filename = f"{output_prefix}.png"

            img.save(filename)
            image_paths.append(filename)

        return image_paths

    def get_text_info(self, text):
        """
        获取文本信息

        Args:
            text: 文本内容

        Returns:
            dict: 包含文本长度、字节数、需要的二维码数量等信息
        """
        text_bytes = text.encode('utf-8')
        max_bytes = self.MAX_BYTES_PER_QR[self.error_correction_level]
        num_qrcodes = math.ceil(len(text_bytes) / max_bytes)

        return {
            'char_count': len(text),
            'byte_count': len(text_bytes),
            'max_bytes_per_qr': max_bytes,
            'num_qrcodes': num_qrcodes,
            'error_correction': self.error_correction_level
        }


def main():
    """命令行测试"""
    converter = TextToQRCode(error_correction='M')

    # 测试短文本
    test_text = "Hello, World! 这是一个测试文本。"
    print(f"测试文本: {test_text}")

    info = converter.get_text_info(test_text)
    print(f"\n文本信息:")
    print(f"  字符数: {info['char_count']}")
    print(f"  字节数: {info['byte_count']}")
    print(f"  需要的二维码数量: {info['num_qrcodes']}")

    paths = converter.text_to_qrcode(test_text, "test_qrcode")
    print(f"\n已生成二维码: {', '.join(paths)}")


if __name__ == "__main__":
    main()
