import os

from flask import Blueprint, render_template
from prometheus_client import Gauge
from prometheus_flask_exporter import PrometheusMetrics

from waves import config
from waves.config import outro_section
from waves.models import Recording

blueprint = Blueprint("waves", __name__)

_metrics = PrometheusMetrics(
    blueprint,
    excluded_paths=[
        "/static/assets/",
        "/static/images/",
    ],
    default_latency_as_histogram=False,
)
_recordings_count_gauge = Gauge(
    "recordings_available_count", "Number of available recordings"
)


def get_artwork_path(path: str) -> str | None:
    for ext in config.ARTWORK_EXTENSIONS:
        artwork_path = path + ext
        if os.path.isfile(artwork_path):
            return artwork_path
    return config.ARTWORK_PLACEHOLDER_PATH


def sanitize_for_html_id(string: str) -> str:
    if string[0].isdigit():
        string = "_" + string
    return string.replace(" ", "_").replace(".", "_").replace("(", "").replace(")", "")


def collect_recordings() -> list[Recording]:
    recording_list: list[Recording] = []
    for file in os.listdir(config.RECORDINGS_PATH):
        path = os.path.join(config.RECORDINGS_PATH, file)
        # Check if file matches any supported audio format
        file_extension = "." + file.split(".")[-1].lower() if "." in file else ""
        if os.path.isfile(path) and file_extension in config.SUPPORTED_AUDIO_FORMATS:
            last_modified_date = os.path.getmtime(path)
            file_no_ext = ".".join(file.split(".")[:-1])
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


@blueprint.route("/")
def index():
    recording_list = collect_recordings()
    _recordings_count_gauge.set(len(recording_list))
    return render_template(
        "index.html",
        sets_list=recording_list,
        site_title=config.SITE_TITLE,
        site_footer=config.SITE_FOOTER,
        site_description=config.SITE_DESCRIPTION,
        outro_section=outro_section,
    )
