import json
import socket
import os
import subprocess
from pathlib import Path

MAX_STREAM_RATE = 1400

COMMAND_PARAMS = {
    'compress_video': [],
    'resize_video': ['width', 'height'],
    'change_aspect_ratio': ['aspect_ratio'],
    'extract_audio': [],
    'create_gif': ['start_time', 'duration'],
}

ffmpeg_commands = {
    "compress_video": "ffmpeg -i {input} -c:v libx264 -crf 23 {output}",
    "resize_video": "ffmpeg -i {input} -vf scale={width}:{height} -c:a copy {output}",
    "change_aspect_ratio": "ffmpeg -i {input} -aspect {aspect_ratio} -c:a copy {output}",
    "extract_audio": "ffmpeg -i {input} -vn -acodec libmp3lame {output}",
    "create_gif": "ffmpeg -i {input} -ss {start_time} -t {duration} -vf \"fps=10,scale=320:-1:flags=lanczos\" {output}",
}

def ffmpeg_process(command_key, input_file, output_file, params):
    if command_key not in ffmpeg_commands:
        raise ValueError(f"Unknown command key: {command_key}")
    
    command = ffmpeg_commands[command_key]
    format_params = {'input': input_file, 'output': output_file}

    # 各コマンド特有のパラメーターを追加
    for param in COMMAND_PARAMS[command_key]:
        if param in params:
            format_params[param] = params[param]
    
    execute_command = command.format(**format_params)
    
    try:
        subprocess.run(execute_command, shell=True, check=True)
        print(f"Command executed successfully: {execute_command}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = '0.0.0.0'
    server_port = 9001
    sock.bind((server_address, server_port))
    sock.listen(1)

    dpath = 'uploaded_file/'
    if not os.path.exists(dpath):
        os.makedirs(dpath)

    while True:
        print("Starting server...")
        connection, _ = sock.accept()
        
        # headerの受信
        header = connection.recv(8)
        json_length = int.from_bytes(header[:2], "big")
        media_type_size = int.from_bytes(header[2:3], "big")
        payload_size = int.from_bytes(header[3:], "big")

        # json_data, media_type, payloadの受信
        data = connection.recv(json_length + media_type_size)
        json_data = data[:json_length]
        media_type = data[json_length:].decode('utf-8')

        json_obj = json.loads(json_data.decode('utf-8'))
        filename = json_obj['filename']
        command = json_obj['command']

        with open(os.path.join(dpath, filename + media_type), 'wb+') as f:
            while payload_size > 0:
                payload = connection.recv(payload_size if payload_size <= MAX_STREAM_RATE else MAX_STREAM_RATE)
                f.write(payload)
                payload_size -= len(payload)


        # ffmpegの処理
        params = {key: json_obj.get(key) for key in COMMAND_PARAMS[command]}
        input_filename = f"{filename}{media_type}"

        if command == 'extract_audio':
            media_type = '.mp3'
        elif command == 'create_gif':
            media_type ='.gif'   

        output_filename = f"processed_{filename}{media_type}"

        input_file = Path("uploaded_file") / input_filename
        output_file = Path("processed_file") / output_filename

        ffmpeg_process(command, input_file, output_file, params)

        # アップロードされた動画の削除
        os.remove(input_file)

if __name__ == '__main__':
    main()