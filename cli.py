#!/usr/bin/env python3
"""
命令行版本的文本转二维码工具
"""

import argparse
import sys
import os
from text_to_qr import TextToQRCode


def read_from_file(filepath):
    """从文件读取文本"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误: 文件 '{filepath}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        sys.exit(1)


def read_from_stdin():
    """从标准输入读取文本"""
    print("请输入文本（输入完成后按 Ctrl+D (Linux/Mac) 或 Ctrl+Z (Windows) 然后回车）:")
    try:
        return sys.stdin.read()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description='将文本转换为二维码图片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 直接输入文本
  python cli.py -t "Hello World"

  # 从文件读取
  python cli.py -f input.txt

  # 从标准输入读取
  python cli.py

  # 指定输出文件名和错误纠正级别
  python cli.py -f input.txt -o myqr -e H

  # 自定义二维码参数
  python cli.py -t "测试" -o test -e M -b 8 -s 15
        """
    )

    parser.add_argument('-t', '--text', type=str,
                        help='要转换的文本内容')
    parser.add_argument('-f', '--file', type=str,
                        help='从文件读取文本')
    parser.add_argument('-o', '--output', type=str, default='qrcode',
                        help='输出文件名前缀（默认: qrcode）')
    parser.add_argument('-e', '--error-correction', type=str,
                        choices=['L', 'M', 'Q', 'H'], default='M',
                        help='错误纠正级别（默认: M）\n'
                             'L: 7%% 纠正能力\n'
                             'M: 15%% 纠正能力\n'
                             'Q: 25%% 纠正能力\n'
                             'H: 30%% 纠正能力')
    parser.add_argument('-b', '--box-size', type=int, default=10,
                        help='每个小方块的像素大小（默认: 10）')
    parser.add_argument('-s', '--border', type=int, default=4,
                        help='边框大小（小方块数量，默认: 4）')
    parser.add_argument('-i', '--info', action='store_true',
                        help='只显示文本信息，不生成二维码')

    args = parser.parse_args()

    # 获取文本内容
    text = None
    if args.text:
        text = args.text
    elif args.file:
        text = read_from_file(args.file)
    else:
        text = read_from_stdin()

    if not text or text.strip() == '':
        print("错误: 文本内容为空")
        sys.exit(1)

    # 创建转换器
    converter = TextToQRCode(
        error_correction=args.error_correction,
        box_size=args.box_size,
        border=args.border
    )

    # 显示文本信息
    info = converter.get_text_info(text)
    print("\n" + "="*50)
    print("文本信息:")
    print("="*50)
    print(f"字符数量: {info['char_count']}")
    print(f"字节数量: {info['byte_count']}")
    print(f"错误纠正级别: {info['error_correction']}")
    print(f"单个二维码最大容量: {info['max_bytes_per_qr']} 字节")
    print(f"需要生成的二维码数量: {info['num_qrcodes']}")

    if info['num_qrcodes'] > 1:
        print(f"\n注意: 文本较长，将被分割成 {info['num_qrcodes']} 个二维码")

    # 如果只是查看信息，则退出
    if args.info:
        sys.exit(0)

    # 生成二维码
    print("\n" + "="*50)
    print("生成二维码中...")
    print("="*50)

    try:
        image_paths = converter.text_to_qrcode(text, args.output)

        print("\n成功生成二维码!")
        print(f"输出文件:")
        for i, path in enumerate(image_paths, 1):
            file_size = os.path.getsize(path)
            print(f"  [{i}] {path} ({file_size:,} 字节)")

        print("\n" + "="*50)
        print("提示:")
        print("="*50)
        if info['num_qrcodes'] > 1:
            print("请按顺序扫描所有二维码以获取完整文本。")
        else:
            print("使用手机扫描二维码即可获取文本内容。")
        print("="*50)

    except Exception as e:
        print(f"\n错误: 生成二维码失败 - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
