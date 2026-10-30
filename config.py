from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class Provider:
    avatar_id: str
    voice_id: str
    avatar_style: str = "normal"
    background: str = "#000000"
    width: int = 1920
    height: int = 1080
    poll_seconds: int = 15
    timeout_minutes: int = 30


@dataclass
class Episode:
    id: str
    title: str
    script: Path


@dataclass
class Config:
    title: str
    output_dir: Path
    provider: Provider
    episodes: list


def load_config(path: str = "series.yaml") -> Config:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    base = Path(path).resolve().parent
    p = data["provider"]
    provider = Provider(**{k: v for k, v in p.items() if k != "name"})
    episodes = [
        Episode(e["id"], e["title"], base / e["script"]) for e in data["episodes"]
    ]
    return Config(
        title=data["series"]["title"],
        output_dir=base / data["series"].get("output_dir", "output"),
        provider=provider,
        episodes=episodes,
    )
