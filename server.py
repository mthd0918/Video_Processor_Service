import socket
import os
from pathlib import Path

"""""
# todo
## 目標: MP4ファイルをCLIを使ってアップロード
### 要件
- すべてのデータが送信されるまで、最大サイズとして 1400 バイトのパケットを使用
- サーバーへ最初に送信される32バイト -> ファイルのバイト数を通知
- 4GB(2^32)までのファイルに対応
- サーバーは受け取ったファイルをmp4ファイルとして解釈、クライアントは送信するファイルがmp4ファイルかどうかチェック
- レスポンスコードで応答、16バイトのメッセージ
"""""

class VideoCompressorServer:
    def __init__(self, server_address='0.0.0.0', server_port=9001):
        self.server_address = server_address
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.server_address, self.server_port))
        self.socket.listen(1)
        print('Starting up on {} port {}'.format(server_address, server_port))

        self.dpath = 'temp'
        if not os.path.exists(self.dpath):
            os.makedirs(self.dpath)

        print(f"self.dpath: {self.dpath}")

    def read_header(self, connection):
        print("***header****")
        header = connection.recv(8)
        filename_length = int.from_bytes(header[:1], "big")
        json_length = int.from_bytes(header[1:3], "big")
        data_length = int.from_bytes(header[4:8], "big")
        stream_rate = 4096
        print(f"filename_lenght: {filename_length}")
        print(f"json_length: {json_length}")
        print(f"data_lenfth: {data_length}")
        print(f"sream_rate: {stream_rate}")
        print("***header****")
        return filename_length, json_length, data_length, stream_rate

    def read_filename(self, connection, filename_length, json_length, data_length):
        print("***from client***")
        filename = connection.recv(filename_length).decode('utf-8')
        print(f"Filename: {filename}")
        
        if json_length != 0:
            raise Exception('JSON data is not currently supported.')

        if data_length == 0:
            raise Exception('No data to read from client.')
        
        print("***from client***")
        return filename
    
    def handle_file_transfer(self, connection, filename, data_length, stream_rate):
            print(f"***Writing file***")
            with open(os.path.join(self.dpath, filename), 'wb+') as f:
                while data_length > 0:
                    data = connection.recv(min(data_length, stream_rate))
                    if not data:
                        print("Connection closed by client")
                        break
                    f.write(data)
                    print(f'received {len(data)} bytes')
                    data_length -= len(data)
                    print(f"Remaining data_length: {data_length}")
            print('Finished downloading the file from client.')
            print(f"***Writing file***")

    def tcp_main(self):
        while True:
            connection, client_address = self.socket.accept()
            try:
                print('connection from', client_address)

                try:
                    filename_length, json_length, data_length, stream_rate = self.read_header(connection)
                    filename = self.read_filename(connection, filename_length, json_length, data_length)
                    self.handle_file_transfer(connection, filename, data_length, stream_rate)
                except Exception as e:
                    print(f'Error during file transfer: {e}')

            except Exception as e:
                print(f'TCP connection error: {e}')
            finally:
                print("Closing current connection")
                connection.close()

if __name__ == '__main__':
    server = VideoCompressorServer()
    server.tcp_main()