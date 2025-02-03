FROM continuumio/miniconda3
LABEL org.opencontainers.image.authors="j.j.m.vansteenbrugge@umcutrecht.nl"
LABEL org.opencontainers.image.source https://github.com/UMCUGenetics/pypgx


RUN apt update && apt install -y build-essential

COPY ./ ./app 
RUN pip install ./app
