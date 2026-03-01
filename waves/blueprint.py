import os

import markdown
import yaml
from flask import Blueprint, render_template
from prometheus_client import Gauge
from prometheus_flask_exporter import PrometheusMetrics

from waves import config
from waves.caching import cache
from waves.models import OutroSection, Recording

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

_outro_section = OutroSection(
    title=os.getenv("WAVES_OUTRO_TITLE"),
    description=os.getenv("WAVES_OUTRO_DESCRIPTION"),
    link_url=os.getenv("WAVES_OUTRO_LINK_URL"),
    link_text=os.getenv("WAVES_OUTRO_LINK_TEXT"),
)


def get_artwork_path(path: str) -> str:
    for ext in config.ARTWORK_EXTENSIONS:
        artwork_path = path + ext
        if os.path.isfile(artwork_path):
            return artwork_path
    return config.ARTWORK_PLACEHOLDER_PATH


def get_yaml_path(path: str) -> str | None:
    """
    Get the path to the YAML configuration file for the recording.
    """
    for ext in config.YAML_EXTENSIONS:
        yaml_path = path + ext
        if os.path.isfile(yaml_path):
            return yaml_path
    return None


def load_yaml_data(path: str) -> dict:
    """
    Load YAML data from the given path.
    """
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
            if not data:
                return {}
            # Process markdown description if present
            if "description" in data and data["description"]:
                data["description"] = markdown.markdown(data["description"])
            return data
    except Exception as e:
        print(f"Error loading yaml {path}: {e}")
        return {}


def sanitize_for_html_id(string: str) -> str:
    if string[0].isdigit():
        string = "_" + string
    return string.replace(" ", "_").replace(".", "_").replace("(", "").replace(")", "")


@cache.cached(key_prefix="recordings_list")
def collect_recordings() -> list[Recording]:
    recording_list: list[Recording] = []
    for file in os.listdir(config.RECORDINGS_PATH):
        path = os.path.join(config.RECORDINGS_PATH, file)
        # Check if file matches any supported audio format
        file_extension = "." + file.split(".")[-1].lower() if "." in file else ""
        if os.path.isfile(path) and file_extension in config.SUPPORTED_AUDIO_FORMATS:
            last_modified_date = os.path.getmtime(path)
            file_no_ext = ".".join(file.split(".")[:-1])

            yaml_path = get_yaml_path(path)
            yaml_data = load_yaml_data(yaml_path) if yaml_path else {}

            recording_list.append(
                Recording(
                    id=sanitize_for_html_id(file_no_ext),
                    name=file_no_ext,
                    path=path,
                    peaks_path=path + ".json",
                    last_modified_date=last_modified_date,
                    artwork_path=get_artwork_path(path),
                    description=yaml_data.get("description"),
                    tags=yaml_data.get("tags"),
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
        outro_section=_outro_section,
    )
