import json
from pathlib import Path

from .config import Config
from .heygen import HeyGenClient
from .scripts import load_scenes


class Manifest:
    """Tracks video_ids/status so re-runs resume instead of re-billing."""

    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text()) if path.exists() else {}

    def get(self, ep_id):
        return self.data.get(ep_id, {})

    def update(self, ep_id, **kw):
        self.data.setdefault(ep_id, {}).update(kw)
        self.path.write_text(json.dumps(self.data, indent=2))


def run(cfg: Config, only=None, dry_run=False, force=False):
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = Manifest(cfg.output_dir / "manifest.json")
    episodes = [e for e in cfg.episodes if not only or e.id in only]
    if not episodes:
        raise SystemExit("No matching episodes.")

    client = None if dry_run else HeyGenClient()

    for ep in episodes:
        scenes = load_scenes(ep.script)
        title = f"{cfg.title} - {ep.title}"
        payload = HeyGenClient.build_payload(title, scenes, cfg.provider)
        words = sum(len(s.split()) for s in scenes)
        print(f"[{ep.id}] {ep.title}: {len(scenes)} scenes, ~{words / 150:.1f} min")

        if dry_run:
            (cfg.output_dir / f"{ep.id}.payload.json").write_text(json.dumps(payload, indent=2))
            print(f"  dry run -> wrote {ep.id}.payload.json")
            continue

        state = manifest.get(ep.id)
        dest = cfg.output_dir / f"{ep.id}.mp4"
        if state.get("status") == "done" and dest.exists() and not force:
            print("  already done, skipping (use --force to redo)")
            continue

        video_id = state.get("video_id") if not force else None
        if not video_id:
            video_id = client.create_video(payload)
            manifest.update(ep.id, video_id=video_id, status="submitted", title=ep.title)
            print(f"  submitted: {video_id}")
        else:
            print(f"  resuming: {video_id}")

        last = {"s": None}

        def tick(st):
            if st != last["s"]:
                print(f"  status: {st}")
                last["s"] = st

        info = client.wait(
            video_id, cfg.provider.poll_seconds, cfg.provider.timeout_minutes, tick
        )
        client.download(info["video_url"], dest)
        manifest.update(
            ep.id,
            status="done",
            file=dest.name,
            duration=info.get("duration"),
            thumbnail=info.get("thumbnail_url"),
        )
        print(f"  saved {dest}")
