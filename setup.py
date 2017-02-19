from setuptools import setup
from touchosc2midi import __version__

requirement_dependency_link_replacements = {
    "git+https://github.com/dsacre/pyliblo.git@33999ca8178a01c720e99856df769f1986c7e912#egg=pyliblo-0.10.0": "pyliblo",
}

install_requires = list(set(
    requirement_dependency_link_replacements.get(requirement.strip(), requirement.strip())
    for requirement in open('requirements.txt') if not requirement.lstrip().startswith('#')
    )
)

dependency_links = list(requirement_dependency_link_replacements.keys())

setup(name='touchosc2midi',
      version=__version__,
      description="TouchOSC Bridge clone in python",
      long_description=open("README.md").read(),
      author="velolala",
      author_email="fiets@einstueckheilewelt.de",
      url="https://github.com/velolala/touchosc2midi",
      license="LICENSE",
      install_requires=install_requires,
      dependency_links=dependency_links,
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
