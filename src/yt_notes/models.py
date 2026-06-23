from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Chapter:
    title: str
    start: float

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Chapter(title=d["title"], start=float(d["start"]))


@dataclass
class VideoMeta:
    video_id: str
    title: str
    channel: str
    duration: float
    description: str
    url: str
    chapters: list[Chapter] = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        d["chapters"] = [c.to_dict() for c in self.chapters]
        return d

    @staticmethod
    def from_dict(d):
        return VideoMeta(
            video_id=d["video_id"],
            title=d["title"],
            channel=d["channel"],
            duration=float(d["duration"]),
            description=d.get("description", ""),
            url=d["url"],
            chapters=[Chapter.from_dict(c) for c in d.get("chapters", [])],
        )


@dataclass
class Segment:
    start: float
    end: float
    text: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Segment(start=float(d["start"]), end=float(d["end"]), text=d["text"])


@dataclass
class Frame:
    timestamp: float
    path: str
    phash: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Frame(timestamp=float(d["timestamp"]), path=d["path"], phash=d["phash"])


@dataclass
class Manifest:
    version: int
    video_id: str
    url: str
    transcript_source: str
    steps: dict
    paths: dict

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Manifest(
            version=int(d["version"]),
            video_id=d["video_id"],
            url=d["url"],
            transcript_source=d["transcript_source"],
            steps=d["steps"],
            paths=d["paths"],
        )
