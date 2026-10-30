import re
from pathlib import Path

MAX_SCENE_CHARS = 5000  # HeyGen per-scene text limit


def load_scenes(path: Path) -> list:
    """Each blank-line-separated paragraph becomes one scene."""
    text = Path(path).read_text(encoding="utf-8").strip()
    scenes = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    scenes = [s for s in scenes if s]
    for i, s in enumerate(scenes, 1):
        if len(s) > MAX_SCENE_CHARS:
            raise ValueError(f"{path}: scene {i} is {len(s)} chars (max {MAX_SCENE_CHARS})")
    if not scenes:
        raise ValueError(f"{path}: script is empty")
    return scenes
