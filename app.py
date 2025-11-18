import os
from dataclasses import dataclass

from flask import Flask, render_template
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge

_RECORDINGS_PATH = "static/recordings"
_ARTWORK_PLACEHOLDER_PATH = "static/images/artwork_placeholder.webp"
_ARTWORK_EXTENSIONS = {".jpg", ".png", ".webp"}
app = Flask(__name__)

_metrics = PrometheusMetrics(
    app,
    excluded_paths=[
        "/static/assets/",
        "/static/images/",
    ],
    default_latency_as_histogram=False,
)
_recordings_count_gauge = Gauge(
    "recordings_available_count", "Number of available recordings"
)


@dataclass
class Recording:
    id: str
    name: str
    path: str
    peaks_path: str
    last_modified_date: float
    artwork_path: str = _ARTWORK_PLACEHOLDER_PATH


def get_artwork_path(path: str) -> str | None:
    for ext in _ARTWORK_EXTENSIONS:
        artwork_path = path + ext
        if os.path.isfile(artwork_path):
            return artwork_path
    return _ARTWORK_PLACEHOLDER_PATH


def sanitize_for_html_id(string: str) -> str:
    if string[0].isdigit():
        string = "_" + string
    return string.replace(" ", "_").replace(".", "_").replace("(", "").replace(")", "")


def collect_recordings():
    recording_list: list[Recording] = []
    for file in os.listdir(_RECORDINGS_PATH):
        path = os.path.join(_RECORDINGS_PATH, file)
        if os.path.isfile(path) and file.endswith(".mp3"):
            last_modified_date = os.path.getmtime(path)
            file_no_ext = file[:-4]
            recording_list.append(
                Recording(
                    id=sanitize_for_html_id(file_no_ext),
                    name=file_no_ext,
                    path=path,
                    peaks_path=path + ".json",
                    last_modified_date=last_modified_date,
                    artwork_path=get_artwork_path(path),
                )
            )
    recording_list.sort(key=lambda x: x.last_modified_date, reverse=True)
    return recording_list


@app.route("/")
def index():
    recording_list = collect_recordings()
    _recordings_count_gauge.set(len(recording_list))
    return render_template("index.html", sets_list=recording_list)


@app.route("/health")
def health():
    return "I'm healthy :)"


if __name__ == "__main__":
    app.run()
