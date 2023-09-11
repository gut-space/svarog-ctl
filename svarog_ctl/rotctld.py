"""
rotctld - python 3 interface to rotctld

This is roughly based on Mark Jessop's code, which is available here:
https://github.com/darksidelemm/rotctld-web-gui/blob/master/rotatorgui.py

For a nice background about the rotctld protocol, see
https://www.mankier.com/1/rotctl#Commands-Rotator_Commands

Author: Tomek Mrugalski
License: MIT
"""

import socket
from socket import AF_INET, SOCK_STREAM
import logging


class Rotctld:
    """ This is python 3 interface to the rotator controler rotctld, part of the excellent
        hamlib library. This class uses python logging."""

    _connected: bool
    _hostname: str
    _port: int

    def __init__(self, hostname: str = "127.0.0.1", port: int = 4533, timeout: int = 3):
        """ Initializes the object, but does not do anything. Before sending any commands,
            please make sure you call connect() first. """

        # Attempt to do some sanity checks here.
        port = int(port)
        if port < 0 or port > 65535:
            raise IndexError("invalid port %s" % port)

        # There's no easy way to sanity check the hostname, as it could be IPv4, IPv6,
        # a hostname or even a FQDN
        self.sock = socket.socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(timeout)
        self._hostname = hostname
        self._port = port
        self._connected = False

    def connected(self) -> bool:
        """ Returns the status of the connection. """
        return self._connected

    def connect(self) -> str:
        """ Attempts to connect to rotctld. If the connection is established,
            it returns the rotator model as a string. """
        self.sock.connect((self._hostname, self._port))
        model = self.get_model()
        if model is None:
            # Timeout!
            self.close()
            raise Exception("Timeout!")
        self._connected = True
        return model

    def close(self):
        """ Closes the connection. """
        self.sock.close()
        self._connected = False

    def send_command(self, cmd: str):
        """ Send a command to the connected rotctld instance,
            and return the return value. """
        if (cmd and len(cmd) > 0 and cmd[-1] != '\n'):
            cmd_safe = cmd + '\n'
        else:
            cmd_safe = cmd

        self.sock.sendall(bytes(cmd_safe, 'utf-8'))
        resp = self.sock.recv(1024)
        if resp is not None:
            resp = resp.decode().strip()

        resp_txt = resp.replace("\n", " ")
        logging.debug("Sent command [%s], received response [%s]", cmd, resp_txt)
        return resp

    def get_model(self):
        """ Get the rotator model from rotctld """
        model = self.send_command("_")
        logging.info("Rotator model reported as %s", model)
        return model

    def norm_az(self, az: float) -> float:
        """Get the normalized (-180.0.. 180) azimuth."""
        return ((az + 180.0) % 360.0) - 180.0

    def norm_el(self, el: float) -> float:
        """Get the normalized (0..90) elevation."""

        # Truncate if necessary
        if el > 90.0:
            el = 90.0
        elif el < 0.0:
            el = 0.0

        return el

    def set_pos(self, azimuth: float, elevation: float):
        """Command rotator to a particular azimuth/elevation.
           Returns a tuple of data (boolean, str), where the first one
           describes if the command was executed correctly and the second
           one the actual response.

            Note the rotators take the command, but they need some
            time to actually rotate. The command response is sent immediately,
            but the antenna rotates for a while. Please use get_pos() to check
            the current antenna rotation."""

        elevation = self.norm_el(elevation)
        azimuth = self.norm_az(azimuth)

        command = "P %3.1f %2.1f" % (azimuth, elevation)
        logging.debug(f"Setting position to {command}")
        resp = self.send_command(command)
        if "RPRT 0" in resp:
            return True, resp
        return False, resp

    def get_pos(self):
        """ Returns the antenna position. Returns a tuple: azimuth and elevation """
        # Send poll command and read in response.
        resp = self.send_command('p')

        # Split the response by \n (az and el are on separate lines)
        try:
            resp_split = resp.split('\n')
            az = float(resp_split[0])
            el = float(resp_split[1])
            return az, el
        except IndexError as e:
            logging.error(f"Could not parse position: {resp}: {e}")
            return None, None

    def stop(self):
        """ Tells the rotator to stop rotating immediately."""
        return self.send_command('S')

    def park(self):
        """Tells the rotator to park itself. Some rotators don't support this operation."""
        return self.send_command('K')

    def capabilities(self):
        """Attempts to get what the rotctld lib knows about this specific backend. Response
           is very much rotctld dependent."""
        return self.send_command('1')
