import socket
import sys
import os

class VideoCompressorClient:
    def __init__(self, server_address='0.0.0.0', server_port=9001):
        self.server_address = server_address
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print('connecting to {}'.format(server_address, server_port))

    def protocol_header(self, filename_length, json_length, data_length):
        return filename_length.to_bytes(1, "big") + json_length.to_bytes(3,"big") + data_length.to_bytes(4,"big")

    def check_file_size(self, file_path):
        with open(file_path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            filesize = f.tell()
            f.seek(0, 0)
        if filesize > pow(2, 32):
            raise ValueError('File must be below 2GB')
        return filesize

    def send_header(self, filename, filesize):
        filename_bits = filename.encode('utf-8')
        header = self.protocol_header(len(filename_bits), 0, filesize)
        self.socket.send(header)
        self.socket.send(filename_bits)

    def send_file_content(self, file_path):
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                print('Sending file data')
                self.socket.send(data)

    def tcp_main(self):
        try:
            self.socket.connect((self.server_address, self.server_port))
            
            file_path = input("Enter file name: ")
            filename = os.path.basename(file_path)
            
            filesize = self.check_file_size(file_path)
            self.send_header(filename, filesize)
            self.send_file_content(file_path)

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