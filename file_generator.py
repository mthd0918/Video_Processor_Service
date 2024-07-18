import os
import string
import random

def generate_random_string(length):
    """指定された長さのランダムな文字列を生成する"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_byte_file(filename):
    """()内でファイルサイズをバイトで指定"""
    content = generate_random_string(4000)

    # ファイルに書き込む
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    # 実際のファイルサイズを確認
    actual_size = os.path.getsize(filename)
    print(f"ファイル '{filename}' を作成しました。")
    print(f"ファイルサイズ: {actual_size} バイト")