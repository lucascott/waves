from dataclasses import dataclass

from waves import config


@dataclass
class Recording:
    """
    Represents a single recording (DJ mix) with its metadata, including paths to the audio file, peaks data, and artwork.
    """

    id: str
    name: str
    path: str
    peaks_path: str
    last_modified_date: float
    artwork_path: str = config.ARTWORK_PLACEHOLDER_PATH
    description: str | None = None
    tags: list[str] | None = None
    tracklist: list[str] | None = None


@dataclass
class OutroSection:
    """
    Represents the optional outro section of the webpage, which can include a title, description, and an external link.
    """

    title: str | None
    description: str | None
    link_url: str | None
    link_text: str | None

    def has_content(self) -> bool:
        return any(
            [
                self.title,
                self.description,
                self.link_url and self.link_text,
            ]
        )

    def normalized_link_text(self) -> str | None:
        """Return the external link text if both URL and text are provided, otherwise return a cleaned version of the URL."""
        if self.link_url and self.link_text:
            return self.link_text
        return (
            self.link_url.replace("https://", "").replace("http://", "")
            if self.link_url
            else None
        )
