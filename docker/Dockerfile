FROM python:2.7

RUN apt-get update &&\
    apt-get install -y liblo-dev librtmidi-dev

RUN pip search touchosc2midi
RUN pip install touchosc2midi --allow-unverified touchosc2midi

ENTRYPOINT ["touchosc2midi"]
