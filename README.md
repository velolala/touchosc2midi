touchosc2midi
==============================================================
> a TouchOSC Bridge clone, aimed at linux, written in python.

Motivation
----------
I wanted to have a TouchOSC Bridge running on a raspberrypi. After researching the options and running into several
deadends, I figured out, I need to write my own. Specifically this program aims to achieve the following:

- it works on linux
- it works on ARM
- it doesn't need the `.touchosc` layout-files
- it can provide virtual midi ports, like the original TouchOSC Bridge from http://hexler.net/software/touchosc
- it is open source
- it advertises the service via `zeroconf`
- it needs minimal configuration

Dependencies
------------
`touchosc2midi` is built on top of these pip-installable packages:

- `pyliblo`
- `mido` (needs `python-rtmidi` and/or(FIXME!) `portmidi`)
- `zeroconf`

and without these, it wouldn't be such an embarrassingly trivial program.

Installation
------------

### Prerequisites
You will need a recent version of `pip` and `cython`

    pip install -U pip
    pip install cython

### From pypi

    pip install touchosc2midi

### From source

    git clone https://github.com/velolala/touchosc2midi
    cd touchosc2midi
    pip install .

`pyliblo` and `python-rtmidi` need some OS libraries installed (i.e. `liblo-dev` and `librtmidi-dev` Debian). Check out https://github.com/velolala/touchosc2midi/tree/master/docker/Dockerfile to see how to install from a plain Debian with python 2.7.

Getting started
---------------
After installation you should have a the `touchosc2midi` script in your path. Start it with

    touchosc2midi

and open the "Midi Bridge" configuration dialog on your TouchOSC device. You should see an entry for your host. Click on your host and click "Done". Now you should have midi in- and out-ports named "TouchOSC Bridge" that you can use with your client software.

Midi Configuration
------------------
This section shows you, how to do more specific midi configurations.

### Backends

Since `touchosc2midi` uses `mido`, it can be configured with several backends (see:
http://mido.readthedocs.org/en/latest/backends.html for details).

By default it tries to mimic the behavior of the original `TouchOSC Bridge` (see: http://hexler.net/software/touchosc); that is: opening virtual in- and out-ports named "TouchOSC Bridge". Therefore, it tries to use an `rtmidi` backend by default, since only this backend allows the creation of virtual midi ports.

Unfortunately, it get's more confusing, because `rtmidi` allows several API's (e.g. 'LINUX_ALSA', 'UNIX_JACK').
The default for `touchosc2midi` is to use the `rtmidi` backend with the first available/implemented API.

If you want to change the backend, the command:

    touchosc2midi list backends

lists the available full backend strings that you can use for the `MIDO_BACKEND=...` environment variable.
To make use of another backend, call `touchosc2midi` like this:

    MIDO_BACKEND=<backend string> touchosc2midi

### Midi Ports

By default `touchosc2midi` uses virtual ports for midi-in and midi-out. You can, however, connect midi-ports directly. The command:

    touchosc2midi list ports

lists all available ports with their ID and their port string. You can connect midi-in and midi-out ports either by ID or by their name string, e.g.:

    touchosc2midi --midi-in=1 --midi-out="iConnectMIDI4+ MIDI 11"

Please note, that it is currently not possible to mix virtual and direct midi ports (but I'd be happy to accept your PR for this!).

OSC Configuration
-----------------
`touchosc2midi` tries to detect your main network interface for the network part automatically and you can expect this to work in most cases. You can, however, make it listen on a specific IP address:

    touchosc2midi --ip=192.168.0.53

Docker
------

The git repository contains a `Dockerfile`. To use it:

    cd docker

    docker build -t touchosc2midi:latest .

Above builds a container with all OS dependencies and `touchosc2midi` installed. When `run`ning, you will need to share the `/dev/snd/seq` device and expose the OSC receiving port, e.g. like this:

    docker run -p 0.0.0.0:12101:12101/udp --device=/dev/snd/seq:/dev/snd/seq touchosc2midi:latest

Note, that when using docker, the `zeroconf` service announcement does not work, so you'll have to configure your ip address manually on the touchOSC device.


License
-------
This program is published under the MIT License. See `LICENSE` for details.
