"""
Author: Travis Hammond
Version: 10_19_2022
"""

from tcp import TCPClient

client = TCPClient('127.0.0.1', 12000)

while True:
    client.send(input('Msg: ').encode())
    print(client.recieve())