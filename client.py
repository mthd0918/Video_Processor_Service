import json
import os
import socket
import sys

class Client:
    MAX_STREAM_RATE = 1400

    COMMAND_LIST = {
        1: {'command': 'compress_video', 'description': 'Compress video'},
        2: {'command': 'resize_video', 'description': 'Change video resolution'},
        3: {'command': 'change_aspect_ratio', 'description': 'Modify video aspect ratio'},
        4: {'command': 'extract_audio', 'description': 'Convert video to audio'},
        5: {'command': 'create_gif', 'description': 'Create GIF from specified time range'},
    }

    COMMAND_PARAMS = {
        'compress_video': [],
        'resize_video': ['width', 'height'],
        'change_aspect_ratio': ['aspect_ratio'],
        'extract_audio': [],
        'create_gif': ['start_time', 'duration'],
    }

    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.server_address, self.server_port))
        except socket.error as err:
            print(err)
            sys.exit(1)
    
    def input_command(self):
        print("************************")
        print("Enter a number...")
        for num, data in self.COMMAND_LIST.items():
            print(f"{num}: {data['description']}")
        print("************************")
        
        while True:
            command_num = int(input("Choose command:"))
            if command_num in self.COMMAND_LIST:
                return self.COMMAND_LIST[command_num]['command']
            else:
                print("Invalid value, choose command 1~5\n")

    def get_command_params(self, command):
        params = {}
        for param in self.COMMAND_PARAMS[command]:
            if param in ['width', 'height']:
                params[param] = input(f"Enter {param} (pixels): ")
            elif param == 'aspect_ratio':
                params[param] = input("Enter aspect ratio (e.g., 16:9): ")
            elif param == 'start_time':
                params[param] = input("Enter start time (format: HH:MM:SS): ")
            elif param == 'duration':
                params[param] = input("Enter duration (seconds): ")
        return params

    def send_file(self, filepath):
        with open(filepath, 'rb') as f:
            f.seek(0, os.SEEK_END)
            filesize = f.tell()
            f.seek(0,0)

            if filesize > pow(2,32):
                raise Exception('File must be below 4GB.')

            full_filename = os.path.basename(f.name)
            filename, media_type = os.path.splitext(full_filename)

            print("filename:", filename)
            print("media_type:", media_type)

            command = self.input_command()
            params = self.get_command_params(command)

            file_info = {
                'filename': filename,
                'command': command,
                **params
            }
            json_data = json.dumps(file_info)

            json_length = len(json_data).to_bytes(2, "big")
            media_type_size = len(media_type).to_bytes(1, "big")
            payload_size = filesize.to_bytes(5, "big")

            json_data_bytes = json_data.encode('utf-8')
            media_type_bytes = media_type.encode('utf-8')

            header = json_length + media_type_size + payload_size
            data = header + json_data_bytes + media_type_bytes
            self.sock.send(data)

            payload = f.read(self.MAX_STREAM_RATE)
            while payload:
                self.sock.send(payload)
                payload = f.read(self.MAX_STREAM_RATE)

            self.sock.send(json_data.encode('utf-8'))

def main():
    client = Client('0.0.0.0', 9001)
    client.connect()
    # filepath = input("Enter filepath to your video")
    filepath = 'media/free-video1-sea-cafinet.mp4'
    client.send_file(filepath)

if __name__ == '__main__':
    main()