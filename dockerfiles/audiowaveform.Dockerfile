FROM ubuntu:noble



RUN apt-get update && apt-get install -y curl gnupg \
  && curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x340A52D0CADFD6CBDBE42FF001615546D84E3796" | gpg --dearmor > /usr/share/keyrings/chris-needham-ppa.gpg \
  && echo "deb [signed-by=/usr/share/keyrings/chris-needham-ppa.gpg] https://ppa.launchpadcontent.net/chris-needham/ppa/ubuntu noble main" > /etc/apt/sources.list.d/chris-needham-ppa.list \
  && apt-get update && apt-get install -y audiowaveform \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \

WORKDIR /tmp
# Install uv and watchdog
ENV PATH="/root/.local/bin:${PATH}"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv python install 3.13
#
RUN uvx --from "watchdog[watchmedo]" watchmedo || true

RUN mkdir -p /monitor

# disable uv's online checks since the image is meant to be used in offline environments and the checks can cause delays
ENV UV_OFFLINE=1

# low pixels-per-second and bits to speed up processing and reduce output file size
CMD ["uvx","--from", "watchdog[watchmedo]", "watchmedo", "shell-command", "--ignore-directories", "--recursive", "--drop", "--pattern", "*.mp3", "--command", "audiowaveform -i \"${watch_src_path}\" -o \"${watch_src_path}.json\" --pixels-per-second 1 --bits 8", "/monitor"]
