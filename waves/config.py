"""Configuration module for the Waves application.

All configuration is loaded from environment variables with sensible defaults.
This enables easy customization for different deployment scenarios.
"""

import os

# Application Settings
SITE_TITLE = os.getenv("WAVES_SITE_TITLE", "Waves ～ My mixes collection")
SITE_DESCRIPTION = os.getenv(
    "WAVES_SITE_DESCRIPTION", "My collection of mixes and DJ sets."
)
SITE_FOOTER = os.getenv("WAVES_SITE_FOOTER", "Made with ♥ by lucascott")

# Path Settings
RECORDINGS_PATH = os.getenv("WAVES_RECORDINGS_PATH", "static/recordings")
ARTWORK_PLACEHOLDER_PATH = os.getenv(
    "WAVES_ARTWORK_PLACEHOLDER_PATH", "static/images/artwork_placeholder.webp"
)


def parse_extensions(extensions_str: str) -> set[str]:
    """
    Parse a comma-separated string of file extensions into a set of extensions with leading dots.

    :param extensions_str: A comma-separated string of file extensions (e.g., "mp3,wav,flac")
    :return: A set of file extensions with leading dots (e.g., {".mp3", ".wav", ".flac"})
    """
    return {f".{ext.strip()}" for ext in extensions_str.split(",")}


# Parse comma-separated audio extensions
_supported_audio_formats_str = os.getenv("WAVES_SUPPORTED_AUDIO_FORMATS", "mp3")
SUPPORTED_AUDIO_FORMATS = parse_extensions(_supported_audio_formats_str)

# Parse comma-separated artwork extensions
_artwork_extensions_str = os.getenv("WAVES_ARTWORK_EXTENSIONS", "jpg,png,webp")
ARTWORK_EXTENSIONS = parse_extensions(_artwork_extensions_str)

# Parse comma-separated yaml extensions
_yaml_extensions_str = os.getenv("WAVES_YAML_EXTENSIONS", "yaml,yml")
YAML_EXTENSIONS = parse_extensions(_yaml_extensions_str)
