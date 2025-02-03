FROM phusion/baseimage:latest
    LABEL org.opencontainers.image.authors="j.j.m.vansteenbrugge@umcutrecht.nl"

RUN apt-get update && apt-get install -y --no-install-recommends \
    python python-pip

RUN pip install .
