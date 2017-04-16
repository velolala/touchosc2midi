FROM python:2.7

RUN apt-get update &&\
    apt-get install -y liblo-dev librtmidi-dev

RUN pip install cython
RUN pip install touchosc2midi

ENTRYPOINT ["touchosc2midi"]
