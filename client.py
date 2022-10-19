"""
Author: Travis Hammond
Version: 10_19_2022
"""

from tcp import TCPClient, create_key_from_password
from time import sleep

password = open('password', 'r').read()
# change salt value: salt = os.urandom(16)
key, _ = create_key_from_password(password, salt=b'\x9f\x1eK\x0bWm\xa3\xc3\xaf\xc5,\xb3+\x83\xe0)')

server_address = 'localhost'
server_port = 8888

funnel_server_address = 'localhost'
funnel_server_port = 13000

while True:
    try:
        # Connect to Actual Server
        client_send = TCPClient(server_address, server_port, timeout=10)
        # Connect to Funnel Server
        client_recieve = TCPClient(funnel_server_address, funnel_server_port, key=key)
        client_recieve.send(b'0001')

        # Attempt connection (above code) again on ConnectionResetError
        reply = b''
        while True:
            code = b'0001'
            reply = client_recieve.recieve()  # ConnectionResetError if funnel server crashed etc.
            if len(reply) == 0:
                break
            reply = reply[4:]
            print('From Funnel Server, Sending and Listening to Actual Server:', reply[:200], '...', reply[-50:])
            reply = client_send.send_recieve(reply)
            print('From Actual Server, Sending and Listening to Funnel Server:', reply[:200], '...', reply[-50:])
            client_recieve.send(code + reply)  # ConnectionResetError if funnel server crashed etc.
    except ConnectionResetError as e:
        client_recieve.close()
        client_send.close()
        print(e)
    except Exception as e:
        client_recieve.close()
        client_send.close()
        print(type(e), e)
