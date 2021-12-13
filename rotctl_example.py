"""
This is a test script for svarog_ctl. It's useful for developers only.
"""


# ROTOR_ADDR = '127.0.0.1'
# ROTOR_PORT = 4533
# BUFFER_SIZE = 1024


# sent = str.encode("p")

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((ROTOR_ADDR, ROTOR_PORT))
# s.send(sent)
# rcvd = s.recv(BUFFER_SIZE)
# s.close()

# print ("sent buffer:", sent)
# print ("received data:", rcvd)

import logging
from svarog_ctl.rotctld import Rotctld

logging.basicConfig(level=logging.INFO)

ctl = Rotctld("127.0.0.1", 4533, 5)

print(f"Connected {ctl.connected()}")
ctl.connect()

print(f"Connected {ctl.connected()}")
model = ctl.get_model()

pos = ctl.get_pos()

ctl.set_pos(20, 10)

pos = ctl.get_pos()

ctl.close()

print(f"Connected {ctl.connected()}")
