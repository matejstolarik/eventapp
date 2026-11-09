from dataclasses import dataclass, field


@dataclass
class RawEvent:
    venue_id: str
    title: str
    date: str           # YYYY-MM-DD, Prague local time
    start_time: str | None  # HH:MM, Prague local time; null if source does not provide it
    end_time: str | None
    doors_time: str | None = None  # HH:MM, door opening time; never used as start_time
    formats: list = field(default_factory=list)
    genres: list = field(default_factory=list)
    character: list = field(default_factory=list)
    artists: list = field(default_factory=list)
    price_text: str | None = None
    free: bool | None = None
    sold_out: bool | None = None  # True only if source explicitly says sold out; False if selling; else None
    room: str | None = None       # room/hall as reported by source (e.g. "Velký sál"); None if not provided
    ticket_url: str | None = None
    image_url: str | None = None
    description: str | None = None         # plain text, max 1000 chars; from source data
    description_source: str | None = None  # "source" if from data, "ai" if AI-generated
    source: dict = field(default_factory=dict)  # {type, url, external_id, section?}
    flags: list = field(default_factory=list)   # pre-detected quality flags from adapter
    status: str = "scheduled"
