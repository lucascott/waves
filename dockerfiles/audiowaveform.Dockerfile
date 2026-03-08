FROM realies/audiowaveform:latest

RUN apk add --no-cache py3-watchdog

RUN mkdir -p /monitor

# low pixels-per-second and bits to speed up processing and reduce output file size
ENTRYPOINT ["watchmedo", "shell-command", "--ignore-directories", "--recursive", "--drop", "--pattern", "*.opus", "--command", "src=\"${watch_src_path}\"; audiowaveform -i \"${src}\" -o \"${src%.*}.json\" --pixels-per-second 1 --bits 8", "/monitor"]
