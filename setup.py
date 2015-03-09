from setuptools import setup
from touchosc2midi import __version__

setup(name='touchosc2midi',
      version=__version__,
      description="TouchOSC Bridge clone in python",
      long_description=open("README.md").read(),
      author="velolala",
      author_email="fiets@einstueckheilewelt.de",
      url="https://github.com/velolala/touchosc2midi",
      license="LICENSE",
      install_requires=["pyliblo",
                        "docopt",
                        "mido",
                        "zeroconf",
                        "python-rtmidi==0.5b1"],
      packages=["touchosc2midi"],
      entry_points={"console_scripts": [
          "touchosc2midi = touchosc2midi.touchosc2midi:main"
                ]
            },
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
          "Topic :: Artistic Software",
          "Topic :: Home Automation",
          "Topic :: Multimedia :: Sound/Audio :: MIDI",
      ]
      )
