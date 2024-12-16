"""
Configuration helper for touchosc2midi.

(c) 2015- velolala <fiets@einstueckheilewelt.de>
"""
import os
import mido
import logging

log = logging.getLogger(__name__)

VIRT_MIDI_PORT = "TouchOSC Bridge"


class ConfigurationError(Exception):
    pass


def get_rtmidi_backends():
    """Return available full (backend + api) mido rtmidi configuration
    options as a list of strings.
    """
    try:
        rtmidi = mido.Backend('mido.backends.rtmidi', load=True)
        return ['mido.backends.rtmidi/' + b for b in rtmidi.module.get_api_names()]
    except ImportError:
        return []


def get_mido_backend():
    """Create the mido backend from environment. Note: if not configured
    in environment it will return the first available API for rtmidi.
    """
    log.debug("MIDO_BACKEND from env: {}".format(os.environ.get('MIDO_BACKEND')))
    if 'MIDO_BACKEND' not in os.environ:
        rtmidi_apis = get_rtmidi_backends()
        if rtmidi_apis:
            os.environ['MIDO_BACKEND'] = rtmidi_apis[0]
    if 'MIDO_BACKEND' in os.environ:
        backend = mido.Backend(os.environ.get('MIDO_BACKEND'), load=True)
        log.debug("Using backend {}.".format(backend))
        return backend
    else:
        return mido


def list_backends():
    """Print the available mido backend configuration strings to stdout.
    """
    log.info('Backends for environment variable MIDO_BACKEND=<...> :')
    for backend in get_rtmidi_backends() + ['mido.backends.portmidi']:
        log.info("\t{}".format(backend))


def list_ports(backend):
    """Print known midi in- and out-ports for the given `backend` to
    stdout.
    """
    log.info("Midi in-ports:")
    for i, port in enumerate(backend.get_input_names()):
        log.info("\t{}: {}".format(i, port))
    log.info("Midi out-ports:")
    for i, port in enumerate(backend.get_output_names()):
        log.info("\t{}: {}".format(i, port))


def configure_ioports(backend, virtual=True, mido_in=None, mido_out=None):
    """Create a midi in and a midi out port on mido backend `backend`. If
    virtual is True, try to create two virtual ports.
    """
    log.debug("Backend for midi is {}.".format(backend))
    midi_in = None
    midi_out = None
    if virtual:
        try:
            # we have to init with dummy callback, there seems to be a bug in mido
            midi_in = backend.open_input(VIRT_MIDI_PORT, virtual=True, callback=lambda x: x)
            midi_out = backend.open_output(VIRT_MIDI_PORT, virtual=True)
            # work around bug in mido prior to 1.3.0
            if backend.api == 'LINUX_ALSA':
                midi_out._rt.set_port_name(VIRT_MIDI_PORT)
        except ImportError:
            log.error("Cannot open virtual IOports. Make sure, rtmidi is available"
                      "or choose another backend.")
            raise ConfigurationError("Cannot open virtual IOports. Make sure, rtmidi"
                                     "is available or choose anoter backend")
    else:
        if mido_in and mido_in.isdigit():
            mido_in = backend.get_input_names()[int(mido_in)]
        if mido_out and mido_out.isdigit():
            mido_out = backend.get_output_names()[int(mido_out)]
        # we have to init with dummy callback, there seems to be a bug in mido
        midi_in = backend.open_input(mido_in, callback=lambda x: x)
        midi_out = backend.open_output(mido_out)
    log.debug("Inport is {}".format(midi_in))
    log.debug("Outport is {}".format(midi_out))
    return midi_in, midi_out
