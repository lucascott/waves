FROM alpine/curl:latest AS downloader
RUN curl -L -O https://github.com/bbc/audiowaveform/releases/download/1.10.1/audiowaveform_1.10.1-1-12_arm64.deb

FROM python:3.12-slim-bookworm

WORKDIR /tmp

RUN apt update \
    && apt install -y libmad0 libsndfile1 libid3tag0 libboost-all-dev \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm audiowaveform_1.10.1-1-12_arm64.deb

COPY --from=downloader /audiowaveform_1.10.1-1-12_arm64.deb .
RUN dpkg -i audiowaveform_1.10.1-1-12_arm64.deb \
    apt -f install -y


RUN pip install "watchdog[watchmedo]"

RUN mkdir -p /monitor

CMD watchmedo shell-command --ignore-directories --recursive --drop --pattern "*.mp3" --command='audiowaveform -i "${watch_src_path}" -o "${watch_src_path}.json" --pixels-per-second 1 -b 8' /monitor
