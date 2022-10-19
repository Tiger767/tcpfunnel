"""
Author: Travis Hammond
Version: 10_19_2022
"""

from tcp import TCPServer

server = TCPServer(14000)

def func(message):
    print(message)
    return b'[' + message + b']'

server.run(func)