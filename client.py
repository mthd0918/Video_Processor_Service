import json
import os
import socket
import sys

MAX_STREAM_RATE = 1400

def input_command():
    command_map = {
        1: 'Compress video',
        2: 'Change video resolution',
        3: 'Modify video aspect ratio',
        4: 'Convert video to audio',
        5: 'Create GIF and WEBM from specified time range',
    }

    print("************************")
    for key, value in command_map.items():
        print(f"{key}: {value}")
    print("************************")
    
    while True:
        command = int(input("Choose command:"))
        if command in command_map:
            return command
        else:
            print("Invalid value, choose command 1~5\n")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = '0.0.0.0'
    server_port = 9001

    try:
        sock.connect((server_address, server_port))
    except socket.error as err:
        print(err)
        sys.exit(1)

    # filepath = input("Enter upload filepath: ")
    filepath = 'media/12041412_1920_1080_25fps.mp4'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             

    with open(filepath, 'rb') as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        f.seek(0,0)

        if filesize > pow(2,32):
            raise Exception('File must be below 4GB.')

        filename = os.path.basename(f.name)
        media_type = os.path.splitext(filename)[1]

        command = input_command()

        file_info = {
            'filename': filename,
            'command': command
        }
        json_data = json.dumps(file_info)

        json_length = len(json_data).to_bytes(2, "big")
        media_type_size = len(media_type).to_bytes(1, "big")
        payload_size = filesize.to_bytes(5, "big")

        header = json_length + media_type_size + payload_size
        
        json_data_bytes = json_data.encode('utf-8')
        media_type_bytes = media_type.encode('utf-8')

        body = json_data_bytes + media_type_bytes

        data = header + body

        sock.send(data)

        print(data)

        payload = f.read(MAX_STREAM_RATE)
        while payload:
            # print("Sending...")
            sock.send(payload)
            payload = f.read(MAX_STREAM_RATE)

        sock.send(json_data.encode('utf-8'))

if __name__ == '__main__':
    main()