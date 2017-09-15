import picamera
import picamera.array as picarray

from time import sleep
import socket
import atexit

import numpy as np
import pickle


host = ''
port = 5560
        
def setup_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    try:
        s.bind((host, port))
    except socket.error as msg:
        print(msg)
    print("Socket created")
    return s

def setup_connection(s):
    s.listen(1)
    print("socket listening")
    conn, address = s.accept()
    print("Connected to {0}:{1}".format(address[0],address[1]))
    return conn

def data_transfer(conn):
    past_picture_str = None
    while True:
        data = conn.recv(1024)
        data = data.decode('utf-8')
        dataMessage = data.split(' ',1)
        command  = dataMessage[0]
        if command == "length":
            past_picture_str = _take_picture_as_np_rgb()
            if past_picture_str is not None:
                reply = str(len(past_picture_str)).ljust(16)
            else:
                print("past picture not taken")
                reply = "0"
        elif command == "picture":
            print("sending picture")
            reply = past_picture_str
        elif command == "kill":
            print("terminating server")
            conn.close()
        elif command == "exit":
             print("client has left")
             break
        else:
            reply = "Not Valid Command"
        print(type(reply))
        if isinstance(reply,str):
            conn.sendall(str.encode(reply))
        else:
            conn.sendall(reply)


def _take_picture_as_np_rgb():
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as output:
            camera.resolution = (1280, 720)
            camera.capture(output,'rgb')
            print("Picture Taken")
            return pickle.dumps(output.array, 0)
         

s = setup_server()

while True:
    try:
        conn = setup_connection(s)
        data_transfer(conn)
    except Exception as e:
        print(e)
        break

