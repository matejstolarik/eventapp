from dataclasses import dataclass, field


@dataclass
class RawEvent:
    venue_id: str
    title: str
    date: str           # YYYY-MM-DD, Prague local time
    start_time: str | None  # HH:MM, Prague local time; null if source does not provide it
    end_time: str | None
    formats: list = field(default_factory=list)
    genres: list = field(default_factory=list)
    character: list = field(default_factory=list)
    artists: list = field(default_factory=list)
    price_text: str | None = None
    free: bool | None = None
    ticket_url: str | None = None
    image_url: str | None = None
    source: dict = field(default_factory=dict)  # {type, url, external_id}
