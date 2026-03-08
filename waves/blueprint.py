import os
from pathlib import Path

import markdown
import yaml
from flask import Blueprint, render_template
from prometheus_client import Gauge

from waves import config
from waves.caching import cache
from waves.models import OutroSection, Recording

blueprint = Blueprint("waves", __name__)

_recordings_count_gauge = Gauge(
    "recordings_available_count", "Number of available recordings"
)

_outro_section = OutroSection(
    title=os.getenv("WAVES_OUTRO_TITLE"),
    description=os.getenv("WAVES_OUTRO_DESCRIPTION"),
    link_url=os.getenv("WAVES_OUTRO_LINK_URL"),
    link_text=os.getenv("WAVES_OUTRO_LINK_TEXT"),
)


def get_artwork_path(base_path: Path) -> Path:
    for ext in config.ARTWORK_EXTENSIONS:
        artwork_path = base_path.with_suffix(ext)
        if artwork_path.is_file():
            return artwork_path
    return Path(config.ARTWORK_PLACEHOLDER_PATH)


def get_yaml_path(base_path: Path) -> Path | None:
    """
    Get the path to the YAML configuration file for the recording.
    """
    for ext in config.YAML_EXTENSIONS:
        yaml_path = base_path.with_suffix(ext)
        if yaml_path.is_file():
            return yaml_path
    return None


def load_yaml_data(path: Path) -> dict:
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
    processed_ids: set[str] = set()
    recordings_path = Path(config.RECORDINGS_PATH)
    for path in recordings_path.iterdir():
        # Check if file matches any supported audio format
        file_extension = path.suffix.lower()
        if path.is_file() and file_extension in config.SUPPORTED_AUDIO_FORMATS and path.stem not in processed_ids:
            file_no_ext = path.stem
            last_modified_date = os.path.getmtime(path)

            yaml_path = get_yaml_path(path)
            yaml_data = load_yaml_data(yaml_path) if yaml_path else {}

            recording_list.append(
                Recording(
                    id=sanitize_for_html_id(file_no_ext),
                    name=file_no_ext,
                    path=str(path),
                    peaks_path=str(path.with_suffix(".json")),
                    last_modified_date=last_modified_date,
                    artwork_path=str(get_artwork_path(path.parent / path.stem)),
                    description=yaml_data.get("description"),
                    tags=yaml_data.get("tags"),
                    tracklist=yaml_data.get("tracklist"),
                )
            )
            processed_ids.add(file_no_ext)
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
