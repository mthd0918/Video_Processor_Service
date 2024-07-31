import json
import socket
import os

MAX_STREAM_RATE = 1400

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = '0.0.0.0'
    server_port = 9001
    sock.bind((server_address, server_port))
    sock.listen(1)

    dpath = 'output/'
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

        print("json_length:", json_length)
        print("media_type_size:", media_type_size)
        print("payload_size:", payload_size)

        # jsonデータの受信
        json_data = connection.recv(json_length)
        json_obj = json.loads(json_data.decode('utf-8'))
        filename = json_obj['filename']
        
        print("json obj: ", json_obj)

        # media_typeの受信
        media_type = connection.recv(media_type_size)

        print("media_type: ",media_type)

        with open(os.path.join(dpath, filename), 'wb+') as f:
            while payload_size > 0:
                payload = connection.recv(payload_size if payload_size <= MAX_STREAM_RATE else MAX_STREAM_RATE)
                print('recieved {} bytes'.format(len(payload)))
                f.write(payload)
                payload_size -= len(payload)
                print(payload_size)

if __name__ == '__main__':
    main()