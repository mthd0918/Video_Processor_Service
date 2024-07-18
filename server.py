import socket
import os
from pathlib import Path

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
        
    def tcp_main(self):
        while True:
            # TCP接続の確立
            connection, client_address = self.socket.accept()
            try:
                print('connection from', client_address)

                # ファイルの受信
                try:
                    # header情報の受け取り
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

                    # クライアントから送られてきた変数の読み取り
                    print("***from client***")
                    filename = connection.recv(filename_length).decode('utf-8')
                    print(f"Filename: {filename}")
                    # 例外処理
                    if json_length != 0:
                        raise Exception('JSON data is not currently supported.')

                    if data_length == 0:
                        raise Exception('No data to read from client.')
                    print("***from client***")

                except Exception as e:
                    print(f'Receiving file error: {e}')

                # 受信したデータをファイルへ書き込み
                try:
                    print(f"***Writing file***")
                    with open(os.path.join(self.dpath, filename),'wb+') as f:
                        # すべてのデータの読み書きが終了するまで、クライアントから読み込まれます
                        while data_length > 0:
                            data = connection.recv(data_length if data_length <= stream_rate else stream_rate)
                            if not data:  # 接続が閉じられた場合
                                print("Connection closed by client")
                                break
                            f.write(data)
                            print('recieved {} bytes'.format(len(data)))
                            data_length -= len(data)
                            print(data_length)

                    print('Finished downloading the file from client.')
                    print(f"***Writing file***")

                except Exception as e:
                    print(f"Writing file error: {e}")

            except Exception as e:
                print(f'TCP connection error: {e}')
            finally:
                print("Closing current connection")
                connection.close()

if __name__ == '__main__':
    server = VideoCompressorServer()
    server.tcp_main()