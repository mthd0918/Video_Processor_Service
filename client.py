import socket
import sys
import os

class VideoCompressorClient:
    def __init__(self, server_address='0.0.0.0', server_port=9001):
        self.server_address = server_address
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print('connecting to {}'.format(server_address, server_port))

    # ヘッダーの作成 引数: bit
    def protocol_header(self, filename_length, json_length, data_length):
        return filename_length.to_bytes(1, "big") + json_length.to_bytes(3,"big") + data_length.to_bytes(4,"big")

    def tcp_main(self):
        # TCP通信開始
        try:
            self.socket.connect((self.server_address, self.server_port))
        except socket.error as err:
            print(err)
            sys.exit(1)
        
        # ファイルの送信
        try:
            filepath = input("Enter file name: ")
            # text_file.txt
            with open(filepath, 'rb') as f:
                # ファイルのサイズチェック
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                f.seek(0,0)

                if filesize > pow(2,32):
                    raise Exception('File must be below 2GB')
                
                # ヘッダーの送信
                filename = os.path.basename(f.name)
                filename_bits = filename.encode('utf-8')
                header = self.protocol_header(len(filename_bits), 0, filesize)
                self.socket.send(header)

                # 4096バイトずつファイルの中身を送信
                data = f.read(4096)
                while data:
                    print('Sending file data')
                    self.socket.send(data)
                    data = f.read(4096)

        except FileNotFoundError as e:
            print(f"File error: {e}")
        except ValueError as e:
            print(f"File size error: {e}")
        except ConnectionError as e:
            print(f"Connection error: {e}")
        except Exception as e:
            print(f"Unexpected error while sending file: {e}")
        finally:
            print('closing socket')
            self.socket.close()

if __name__ == '__main__':
    client = VideoCompressorClient()
    client.tcp_main()