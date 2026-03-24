from typing_extensions import TypedDict


class Subtitle(TypedDict):
    start: float
    end: float
    text: str
    top: bool


class Attachment(TypedDict):
    variant: str
    mime: str
    path: str


class Attachments(TypedDict):
    video: list[Attachment]
    image: list[Attachment]
    subtitle: list[Attachment]


type Tags = dict[str, list[str]]


class Track(TypedDict):
    id: str
    duration: float
    tags: Tags
    attachments: Attachments
