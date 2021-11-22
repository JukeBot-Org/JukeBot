FROM python:3.9.5-slim

RUN apt-get update && apt-get install -y ffmpeg

RUN mkdir -p /jukebot
COPY . /jukebot
WORKDIR jukebot
RUN pip3 install -r requirements.txt

RUN sh -c "chmod +x /jukebot/docker-entrypoint.sh"
ENTRYPOINT ["./docker-entrypoint.sh"]