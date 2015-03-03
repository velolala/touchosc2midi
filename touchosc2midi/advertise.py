#!/usr/bin/env python
"""
Announce touchSCO-MIDI bridge via zeroconf.

(c) 2015 velolala <fiets@einstueckheilewelt.de>
"""
import socket
from time import sleep
from zeroconf import Zeroconf, ServiceInfo
import logging
log = logging.getLogger(__name__)

TOUCHOSC_BRIDGE = '_touchoscbridge._udp.local.'
PORT = 12101


def main_ip():
    """
    '192.0.2.0' is defined TEST-NET in RFC 5737,
    so there *shouldn't* be custom routing for this.

    :return: the IP of the default route's interface.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("192.0.2.0", 0))
    ip = sock.getsockname()[0]
    log.debug("Assuming {} for main route's IP.".format(ip))
    sock.close()
    return ip


def build_service_info(ip):
    """Create a zeroconf ServiceInfo for touchoscbridge
    on for `ip` or the guessed default route interface's IP.
    """
    return ServiceInfo(type=TOUCHOSC_BRIDGE,
                       name="{}.{}".format(socket.gethostname(), TOUCHOSC_BRIDGE),
                       address=socket.inet_aton(ip),
                       port=PORT,
                       properties=dict(),
                       server=socket.gethostname() + '.local.')


class Advertisement(object):
    def __init__(self, ip=None):
        """
        :ip: if string `ip` given, register on given IP
             (if None: default route's IP).
        """
        self.zeroconf = Zeroconf()
        self.info = build_service_info(ip=ip or main_ip())

    def register(self):
        """Registers the service on the network.
        """
        self.zeroconf.register_service(self.info)
        log.debug("Registered {} on {}:{}".format(self.info.name,
                                                   self.ip,
                                                   self.info.port))

    def unregister(self):
        """Unregisters the service.
        """
        self.zeroconf.unregister_service(self.info)
        log.debug("Unregistered touchoscbridge.")

    def update(self, ip=None):
        """Re-register the the service on the network.

        :ip: if string `ip` is given, use given IP when registering.
        """
        self.unregister()
        self.info = build_service_info(ip=ip or main_ip())
        self.register()

    def close(self):
        """Free resources.
        Advertisement.unregister() should be called before closing.
        """
        self.zeroconf.close()

    def get_ip(self):
        """:return: the service's IP as a string.
        """
        return socket.inet_ntoa(self.info.address)

    ip = property(get_ip)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    service = Advertisement()
    try:
        service.register()
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        service.unregister()
        service.close()
