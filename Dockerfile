FROM python:3.9.5-slim

RUN mkdir -p /jukebox
COPY . /jukebox
WORKDIR jukebox
RUN pip3 install -r requirements.txt

ENTRYPOINT ["./docker-entrypoint.sh"]