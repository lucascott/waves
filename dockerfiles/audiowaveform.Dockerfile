FROM alpine/curl:latest AS downloader
RUN curl -L -O https://github.com/bbc/audiowaveform/releases/download/1.10.1/audiowaveform_1.10.1-1-12_amd64.deb

FROM python:3.12-slim-bookworm

WORKDIR /tmp

RUN apt-get update \
    && apt-get install -y libmad0 libsndfile1 libid3tag0 libboost-all-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=downloader /audiowaveform_1.10.1-1-12_amd64.deb .
RUN dpkg -i audiowaveform_1.10.1-1-12_amd64.deb \
    && apt-get -f install -y \
    && rm audiowaveform_1.10.1-1-12_amd64.deb

RUN pip install "watchdog[watchmedo]"

RUN mkdir -p /monitor

CMD watchmedo shell-command --ignore-directories --recursive --drop --pattern "*.mp3" --command='audiowaveform -i "${watch_src_path}" -o "${watch_src_path}.json" --pixels-per-second 1 -b 8' /monitor
