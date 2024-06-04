import os
from dataclasses import dataclass

from flask import Flask, render_template

_RECORDINGS_PATH = 'static/recordings'
_ARTWORK_PLACEHOLDER_PATH = 'static/artwork_placeholder.webp'
app = Flask(__name__)


@dataclass
class Recording:
    id: str
    name: str
    path: str
    peaks_path: str
    artwork_path: str
    last_modified_date: float


def get_artwork_path(path: str) -> str | None:
    artwork_path = path + '.jpg'
    return artwork_path if os.path.exists(artwork_path) else _ARTWORK_PLACEHOLDER_PATH


def sanitize_for_html_id(string: str) -> str:
    if string[0].isdigit():
        string = '_' + string
    return string.replace(' ', '_').replace('.', '_')


def collect_recordings():
    recording_list: list[Recording] = []
    for file in os.listdir(_RECORDINGS_PATH):
        path = os.path.join(_RECORDINGS_PATH, file)
        if os.path.isfile(path) and file.endswith('.mp3'):
            last_modified_date = os.path.getmtime(path)
            file_no_ext = file[:-4]
            recording_list.append(
                Recording(
                    id=sanitize_for_html_id(file_no_ext),
                    name=file_no_ext,
                    path=path,
                    peaks_path=path + '.json',
                    artwork_path=get_artwork_path(path),
                    last_modified_date=last_modified_date,
                )
            )
    recording_list.sort(key=lambda x: x.last_modified_date, reverse=True)
    return recording_list


@app.route('/')
def index():
    return render_template('index.html', sets_list=collect_recordings())


if __name__ == '__main__':
    app.run()
