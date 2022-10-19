"""
Author: Travis Hammond
Version: 10_19_2022
"""

from socket import *
import ssl
from time import sleep

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

BUFFER = 1024


def create_key_from_password(password, salt=None):
    # https://cryptography.io/en/latest/fernet/
    password = password.encode('ascii')
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key, salt


class TCPServer:
    def __init__(self, port) -> None:
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(('', port))
        self.socket.listen(1)

    def run(self, function):
        while True:
            connection_socket, client_address = self.socket.accept()

            #connection_socket = ssl.wrap_socket(connection_socket, server_side=True, certfile='cert.pem')

            while True:
                message = b''
                while True:
                    msg_part = connection_socket.recv(BUFFER)
                    message += msg_part
                    if len(msg_part) < BUFFER:
                        break
                if len(message) == 0:
                    break
                reply = function(message)
                connection_socket.sendall(reply)

            connection_socket.close()

    def close(self):
        self.socket.close()


class TCPSServer:
    def __init__(self, port, key=None) -> None:
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(('', port))
        self.socket.listen(1)
        self.key = key
        if self.key is not None:
            self.fernet = Fernet(self.key)

    def accept(self):
        self.connection_socket, self.client_address = self.socket.accept()

    def recieve(self):
        message = b''
        while True:
            msg_part = self.connection_socket.recv(BUFFER)
            message += msg_part
            if len(msg_part) < BUFFER:
                break
        if self.key is not None:
            message = self.fernet.decrypt(message)
        return message

    def send(self, message):
        if self.key is None:
            self.connection_socket.sendall(message)
        else:
            self.connection_socket.sendall(self.fernet.encrypt(message))

    def send_recieve(self, message):
        self.send(message)
        return self.recieve()

    def close_connection(self):
        self.connection_socket.close()

    def close(self):
        self.socket.close()


class TCPClient:
    def __init__(self, server_ip, server_port, retry_sleep=5, timeout=None, use_ssl=False, key=None) -> None:
        while True:
            try:
                if use_ssl:
                    context = ssl.SSLContext() # ssl.PROTOCOL_TLSv1
                    self.socket = context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname=server_ip)
                    self.socket.connect((server_ip, server_port))
                else:
                    self.socket = socket(AF_INET, SOCK_STREAM)
                    self.socket.connect((server_ip, server_port))
                break
            except ConnectionRefusedError as e:
                print(e)
                sleep(retry_sleep)
        if timeout is not None:
            self.socket.settimeout(timeout)
        self.key = key
        if self.key is not None:
            self.fernet = Fernet(self.key)


    def send(self, message):
        if self.key is None:
            self.socket.sendall(message)
        else:
            self.socket.sendall(self.fernet.encrypt(message))

    def recieve(self):
        message = b''
        while True:
            msg_part = self.socket.recv(BUFFER)
            message += msg_part
            if len(msg_part) < BUFFER:
                break
        print(message[:256])
        if self.key is not None:
            message = self.fernet.decrypt(message)
        return message

    def send_recieve(self, message):
        self.send(message)
        try:
            return self.recieve()
        except timeout as e:
            self.send(message)
            return self.recieve()

    def close(self):
        self.socket.close()
