"""
Author: Travis Hammond
Version: 10_19_2022
"""

from http import client
from tcp import TCPServer, TCPSServer, create_key_from_password

password = open('password', 'r').read()
# change salt value (must match client): salt = os.urandom(16)
key, _ = create_key_from_password(password, salt=b'\x9f\x1eK\x0bWm\xa3\xc3\xaf\xc5,\xb3+\x83\xe0)')

funnel_port = 13000
client_port = 12000

while True:
    try:
        server_send = TCPSServer(funnel_port, key=key)
        server_recieve = TCPServer(client_port)

        def func(message):
            global server_send
            code = b'0001'
            print('From Client, Sending and Listening to Funnel Client:', message[:200], '...', message[-50:])
            reply = server_send.send_recieve(code + message) # ConnectionResetError client crashed etc.
            if len(reply) == 0:
                raise ConnectionResetError()
            reply = reply[4:]
            print('From Funnel Client, Sending and Listening to Client:', reply[:200], '...', message[-50:])
            return reply

        server_send.accept()
        print('accepted:', server_send.recieve())  # ConnectionResetError client crashed etc.
        server_recieve.run(func)
    except ConnectionResetError as e:
        print(e)
        server_send.close()
        server_recieve.close()
    except Exception as e:
        print(e)
        server_send.close()
        server_recieve.close()
