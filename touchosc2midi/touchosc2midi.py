#!/usr/bin/env python
"""
touchosc2midi -- a TouchOSC to Midi Bridge.

Usage:
    touchosc2midi --help
    touchosc2midi list (backends | ports) [-v]
    touchosc2midi [(--midi-in <in> --midi-out <out>)] [--ip <oscserveraddress>] [-v]

Options:
    -h, --help                          Show this screen.
    --midi-in=<in>                      Full name or ID of midi input port.
    --midi-out=<out>                    Full name of or ID midi output port.
    --ip=<oscserveraddress>             Network address for OSC server (default: guess).
    -v, --verbose                       Verbose output.
"""

from __future__ import absolute_import

import logging
import socket
import time

import liblo
import mido

from docopt import docopt

from . import __version__
from .advertise import PORT, default_route_interface, Advertisement
from .configuration import list_backends, list_ports, configure_ioports, get_mido_backend


log = logging.getLogger(__name__)


def message_from_oscsysexpayload(payload):
    """Convert the OSC string into a mido sysex message.
    """
    payload = payload.lower()

    if len(payload) < 2:
        raise ValueError("sysex too short")
    elif not payload.startswith('f0'):
        raise ValueError("sysex doesn't start with F0")
    elif not payload.endswith('f7'):
        raise ValueError("sysex doesn't end with F7")

    sysex = tuple(int(payload[i:i + 2], 16) for i in range(0, len(payload), 2))

    return mido.Message('sysex', data=sysex[1:-1])


def message_from_oscmidipayload(bites):
    """Convert the last 4 OSC-midi bytes into a mido message.
    """
    bites = bites[::-1][0:4]
    return mido.parse(bites)


def message_to_oscmidipayload(message):
    """OSC 1.0 specs: 'Bytes from MSB to LSB are: port id, status byte, data1, data2'
    However, touchOSC seems to be: port id, data2, data1, status byte
    """
    # FIXME: port-id is 0?
    bites = [0] + message.bytes()
    assert len(bites) == 4
    return (bites[0], bites[3], bites[2], bites[1])


def message_to_oscsysexpayload(message):
    """Convert a sysex message into an OSC payload string.
    """
    return message.hex().replace(' ', '')


class OscHandler(object):
    def __init__(self, sink):
        self.sink = sink

    def on_osc(self, path, args, types, src):
        log.debug("OSC received from: {}:{} UDP: {} URL: {}".format(
            src.get_hostname(),
            src.get_port(),
            src.get_protocol() == liblo.UDP,
            src.get_url()))

        if path == '/midi' and types == 'm':
            log.debug("received /midi,m with arg {}".format(args[0]))
            msg = message_from_oscmidipayload(args[0])
        elif path == '/sysex' and types == 's':
            log.debug("received /sysex,s with arg {}".format(args[0]))
            msg = message_from_oscsysexpayload(args[0])

        log.debug("Sending MIDI message {}".format(msg))
        self.sink.send(msg)


class MidiHandler(object):
    def __init__(self, target):
        self.target = target

    def on_midi(self, message):
        if message.type == "clock":
            return

        log.debug("MIDI received: {}".format(message))

        if message.type == "sysex":
            addr = '/sysex'
            arg = ('s', message_to_oscsysexpayload(message))
        else:
            addr = '/midi'
            arg = ('m', message_to_oscmidipayload(message))

        osc = liblo.Message(addr, arg)
        log.debug("Sending OSC {}, {} to: {}:{} UDP: {} URL: {}".format(
            addr,
            arg,
            self.target.get_hostname(),
            self.target.get_port(),
            self.target.get_protocol() == liblo.UDP,
            self.target.get_url()))
        liblo.send(self.target, osc)


def wait_for_target_address(ip=None):
    """Waits for a byte on the OSC-PORT to arrive.
    Extract the sender IP-address, this will become our OSC target.
    """
    log.info("Waiting for first package from touchOSC in order to setup target address...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip or default_route_interface(), PORT))
    _, (address, _) = s.recvfrom(1)
    return address


def main():
    options = docopt(__doc__, version=__version__)
    logging.basicConfig(level=logging.DEBUG if options.get('--verbose') else logging.INFO,
                        format="%(message)s")
    log.debug("Options from cmdline are {}".format(options))
    backend = get_mido_backend()
    if options.get('list'):
        if options.get('backends'):
            list_backends()
        elif options.get('ports'):
            list_ports(backend)
    else:
        try:
            server = None
            midi_in, midi_out = configure_ioports(
                backend,
                virtual=not (options.get('--midi-in') or
                             options.get('--midi-out')),
                mido_in=options.get('--midi-in'),
                mido_out=options.get('--midi-out')
            )

            psa = Advertisement(ip=options.get('--ip'))
            psa.register()

            target_address = wait_for_target_address(psa.ip)

            log.debug("Listening for touchOSC on {}:{}.".format(psa.ip, PORT))
            server = liblo.ServerThread(PORT)
            osc_handler = OscHandler(midi_out)
            server.add_method('/midi', 'm', osc_handler.on_osc)
            server.add_method('/sysex', 's', osc_handler.on_osc)

            target = liblo.Address(target_address, PORT + 1, liblo.UDP)
            log.info("Will send to {}.".format(target.get_url()))

            midi_handler = MidiHandler(target)
            midi_in.callback = midi_handler.on_midi

            log.info("Listening for midi at {}.".format(midi_in))
            server.start()
            while True:
                time.sleep(.0001)
        except KeyboardInterrupt:
            psa.unregister()
            psa.close()
            if server:
                server.stop()
                server.free()
            midi_in.close()
            log.info("closed all ports")


if __name__ == '__main__':
    main()
