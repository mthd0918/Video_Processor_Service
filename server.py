import json
import socket
import os
import subprocess
from pathlib import Path

class VideoServer:
    MAX_STREAM_RATE = 1400

    COMMAND_PARAMS = {
        'compress_video': [],
        'resize_video': ['width', 'height'],
        'change_aspect_ratio': ['aspect_ratio'],
        'extract_audio': [],
        'create_gif': ['start_time', 'duration'],
    }

    FFMPEG_COMMANDS = {
        "compress_video": "ffmpeg -i {input} -c:v libx264 -crf 23 {output}",
        "resize_video": "ffmpeg -i {input} -vf scale={width}:{height} -c:a copy {output}",
        "change_aspect_ratio": "ffmpeg -i {input} -aspect {aspect_ratio} -c:a copy {output}",
        "extract_audio": "ffmpeg -i {input} -vn -acodec libmp3lame {output}",
        "create_gif": "ffmpeg -i {input} -ss {start_time} -t {duration} -vf \"fps=10,scale=320:-1:flags=lanczos\" {output}",
    }

    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.server_address, self.server_port))
        self.sock.listen(1)

        dpath = 'uploaded_file/'
        if not os.path.exists(dpath):
            os.makedirs(dpath)

        while True:
            print("Starting server...")
            connection, _ = self.sock.accept()
            self.handle_client(connection)

    def handle_client(self, connection):
        header = connection.recv(8)
        json_length = int.from_bytes(header[:2], "big")
        media_type_size = int.from_bytes(header[2:3], "big")
        payload_size = int.from_bytes(header[3:], "big")

        data = connection.recv(json_length + media_type_size)
        json_data = data[:json_length]
        media_type = data[json_length:].decode('utf-8')

        json_obj = json.loads(json_data.decode('utf-8'))
        filename = json_obj['filename']
        command = json_obj['command']

        dpath = 'uploaded_file/'
        with open(os.path.join(dpath, filename + media_type), 'wb+') as f:
            while payload_size > 0:
                payload = connection.recv(payload_size if payload_size <= self.MAX_STREAM_RATE else self.MAX_STREAM_RATE)
                f.write(payload)
                payload_size -= len(payload)

        params = {key: json_obj.get(key) for key in self.COMMAND_PARAMS[command]}
        input_filename = f"{filename}{media_type}"

        if command == 'extract_audio':
            media_type = '.mp3'
        elif command == 'create_gif':
            media_type ='.gif'   

        output_filename = f"{command}_processed_{filename}{media_type}"

        input_file = Path("uploaded_file") / input_filename
        output_file = Path("processed_file") / output_filename

        self.ffmpeg_process(command, input_file, output_file, params)

        os.remove(input_file)

    def ffmpeg_process(self, command_key, input_file, output_file, params):
        if command_key not in self.FFMPEG_COMMANDS:
            raise ValueError(f"Unknown command key: {command_key}")
        
        command = self.FFMPEG_COMMANDS[command_key]
        format_params = {'input': input_file, 'output': output_file}

        for param in self.COMMAND_PARAMS[command_key]:
            if param in params:
                format_params[param] = params[param]
        
        execute_command = command.format(**format_params)
        
        try:
            subprocess.run(execute_command, shell=True, check=True)
            print(f"Command executed successfully: {execute_command}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

def main():
    server = VideoServer('0.0.0.0', 9001)
    server.start()

if __name__ == '__main__':
    main()